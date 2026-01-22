#!/usr/bin/env python3

"""

export SPOTIFY_CLIENT_ID="##REMOVED_SPOTIFY_CLIENT_ID"
export SPOTIFY_CLIENT_SECRET="##REMOVED_SPOTIFY_CLIENT_SECRET"
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"

"""


"""
spotify_to_youtube.py

Prototype: convert a Spotify playlist's tracks to YouTube video URLs without using the
YouTube Data API. This uses yt-dlp's search extractor (ytsearch) to find the top YouTube
result for each track.

Usage:
  set -x SPOTIFY_CLIENT_ID <id>
  set -x SPOTIFY_CLIENT_SECRET <secret>
  set -x SPOTIFY_REDIRECT_URI http://127.0.0.1:8888/callback
  /home/shady/Scripts/.venv/bin/python /home/shady/Scripts/spotify_to_youtube.py --playlist PLAYLIST_ID --out out.csv

Notes:
- This avoids the YouTube API by using yt-dlp to search YouTube. yt-dlp scrapes/searches YouTube and is robust for many cases.
- Matching heuristics are simple: search "{track} - {artist}" and pick the first ytsearch result.
- For better accuracy, we could add fuzzy matching and duration checks. This can be extended later.
"""

import os
import csv
import sys
import time
import logging
from typing import List
import re

try:
    import requests
except Exception:
    requests = None

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except Exception:
    spotipy = None

try:
    import yt_dlp
except Exception:
    yt_dlp = None

LOG = logging.getLogger('spotify_to_youtube')


def get_spotify_client(scope='playlist-read-private'):
    if spotipy is None:
        raise RuntimeError('spotipy is not installed in the environment')
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError('Set SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET and SPOTIFY_REDIRECT_URI in env')
    auth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, open_browser=True)
    sp = spotipy.Spotify(auth_manager=auth)
    return sp


def fetch_playlist_tracks(sp, playlist_id: str, limit=None) -> List[dict]:
    tracks = []
    offset = 0
    page_size = 100
    while True:
        batch = sp.playlist_items(playlist_id, offset=offset, limit=page_size, fields='items.track(id,name,artists,duration_ms),next,total')
        items = batch.get('items', [])
        if not items:
            break
        for it in items:
            track = it.get('track')
            if track is None:
                continue
            tracks.append(track)
            if limit and len(tracks) >= limit:
                return tracks
        if not batch.get('next'):
            break
        offset += page_size
    return tracks


def fetch_playlist_tracks_web_fallback(sp, playlist_id_or_url: str, limit=None) -> List[dict]:
    """Fallback: fetch the open.spotify.com playlist page HTML and extract spotify:track:IDs
    then use sp.track(id) to get full track objects. This works for public playlists embedded
    in the web page when the playlist API endpoint is inaccessible.
    """
    if requests is None:
        raise RuntimeError('requests is not installed for web-fallback')
    # Build URL if user passed only an ID
    pid = playlist_id_or_url
    if not pid.startswith('http'):
        pid = f'https://open.spotify.com/playlist/{pid}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    LOG.info('Attempting web fallback: fetching playlist page %s', pid)
    try:
        r = requests.get(pid, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        LOG.debug('Web fetch failed for %s: %s', pid, e)
        return []
    html = r.text
    ids = []
    # try several patterns to be robust against encoding/escaping
    patterns = [
        (r'spotify:track:([A-Za-z0-9]{22})', 'spotify:track'),
        (r'spotify%3Atrack%3A([A-Za-z0-9]{22})', 'url-encoded spotify:track'),
        (r'"uri"\s*:\s*"spotify:track:([A-Za-z0-9]{22})"', 'json uri'),
        (r'"id"\s*:\s*"([A-Za-z0-9]{22})"', 'json id'),
    ]

    # also try a unicode-escaped decode of the JS blobs which sometimes escape ':' as \u003A
    try:
        unescaped = html.encode('utf-8').decode('unicode_escape')
    except Exception:
        unescaped = html

    for pattern, label in patterns:
        found = set(m.group(1) for m in re.finditer(pattern, html))
        # include matches from unescaped variant
        if unescaped is not html:
            found |= set(m.group(1) for m in re.finditer(pattern, unescaped))
        if found:
            LOG.debug('Web-fallback pattern "%s" found %d ids', label, len(found))
        for tid in found:
            if tid not in ids:
                ids.append(tid)
                if limit and len(ids) >= limit:
                    break

    # final attempt: generic spotify:track: (variable-length) if nothing found yet
    if not ids:
        for m in re.finditer(r'spotify:track:([A-Za-z0-9]+)', html):
            tid = m.group(1)
            if tid not in ids:
                ids.append(tid)
                if limit and len(ids) >= limit:
                    break

    # extra permissive attempt: sometimes ids appear in attributes like aria-labelledby
    if not ids:
        for m in re.finditer(r'spotify:track:([A-Za-z0-9]{8,24})', html):
            tid = m.group(1)
            if tid not in ids:
                ids.append(tid)
                if limit and len(ids) >= limit:
                    break

    # If still nothing, write a debug copy of the page for inspection
    if not ids:
        try:
            dbg_dir = os.path.join(os.path.dirname(__file__), 'spotify_debug')
            os.makedirs(dbg_dir, exist_ok=True)
            out_file = os.path.join(dbg_dir, f'playlist_{playlist_id_or_url.replace("/","_")}.html')
            with open(out_file, 'w', encoding='utf-8') as fh:
                fh.write(html)
            LOG.warning('Web-fallback found 0 ids; page HTML written to %s for inspection', out_file)
        except Exception as e:
            LOG.debug('Failed to write debug HTML: %s', e)

    LOG.info('Web fallback found %d unique track ids on page', len(ids))
    # If we still have no ids, try fetching the embed page which sometimes contains track URIs
    if not ids:
        embed_url = None
        try:
            # If the input was an ID, build the embed URL; if it was a full URL, extract the id
            pid = playlist_id_or_url
            if pid.startswith('http'):
                pid = extract_playlist_id(pid)
            embed_url = f'https://open.spotify.com/embed/playlist/{pid}'
            LOG.info('Attempting embed page fallback: fetching %s', embed_url)
            r2 = requests.get(embed_url, headers=headers, timeout=12)
            if r2.status_code == 200:
                html2 = r2.text
                for m in re.finditer(r'spotify:track:([A-Za-z0-9]{22})', html2):
                    tid = m.group(1)
                    if tid not in ids:
                        ids.append(tid)
                        if limit and len(ids) >= limit:
                            break
                if ids:
                    LOG.info('Embed fallback found %d ids', len(ids))
                else:
                    dbg_file = os.path.join(os.path.dirname(__file__), 'spotify_debug', f'playlist_embed_{pid}.html')
                    try:
                        with open(dbg_file, 'w', encoding='utf-8') as fh:
                            fh.write(html2)
                        LOG.warning('Embed fallback returned 0 ids; embed page written to %s', dbg_file)
                    except Exception:
                        LOG.debug('Failed to write embed debug file', exc_info=True)
        except Exception:
            LOG.debug('Embed fallback failed', exc_info=True)
    tracks = []
    for tid in ids:
        try:
            track = sp.track(tid)
        except Exception as e:
            LOG.debug('sp.track failed for %s: %s', tid, e)
            continue
        if track:
            tracks.append(track)
        if limit and len(tracks) >= limit:
            break
        # small delay to avoid rate limits
        time.sleep(0.1)
    return tracks


def extract_playlist_id(maybe_url: str) -> str:
    """If input is a Spotify playlist URL or URI, extract the playlist id; otherwise return input."""
    if not maybe_url:
        return maybe_url
    # spotify:playlist:ID
    if maybe_url.startswith('spotify:'):
        parts = maybe_url.split(':')
        if len(parts) >= 3:
            return parts[-1]
    # web url
    # examples: https://open.spotify.com/playlist/{id}?si=...
    try:
        if 'open.spotify' in maybe_url or 'spotify.com' in maybe_url:
            # split by / and take the segment after 'playlist'
            parts = maybe_url.split('/')
            if 'playlist' in parts:
                idx = parts.index('playlist')
                if idx + 1 < len(parts):
                    pid = parts[idx + 1].split('?')[0]
                    return pid
    except Exception:
        pass
    return maybe_url


def build_query(track: dict) -> str:
    name = track.get('name', '')
    artists = track.get('artists', [])
    artist = artists[0].get('name') if artists else ''
    # Basic query: "Song Title - Artist"
    return f"{name} - {artist}"


def search_youtube(query: str, timeout=10):
    if yt_dlp is None:
        raise RuntimeError('yt-dlp is not installed in the environment')
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # use ytsearch1: to get first match
        search = f"ytsearch1:{query}"
        try:
            res = ydl.extract_info(search, download=False)
        except Exception as e:
            LOG.debug('yt-dlp search failed for query %s: %s', query, e)
            return None
        # res contains 'entries' for ytsearch
        entries = res.get('entries') if isinstance(res, dict) else None
        if entries:
            return entries[0]
        # Sometimes extract_info returns a single dict
        if isinstance(res, dict) and res.get('id'):
            return res
        return None


def spotify_playlist_to_csv(playlist_id: str, playlist_name:str, out_path: str, out_path_playlist: str, max_tracks=None, dry_run=False):
    sp = get_spotify_client()
    # fetch tracks with error handling for not-found/private playlists
    try:
        tracks = fetch_playlist_tracks(sp, playlist_id, limit=max_tracks)
    except Exception as e:
        # Try to get playlist metadata to provide a clearer error
        try:
            sp.playlist(playlist_id)
        except Exception:
            LOG.warning('sp.playlist failed for %s: %s -- attempting web-fallback', playlist_id, e)
            # attempt web fallback even if the playlist API reports not-found
            try:
                tracks = fetch_playlist_tracks_web_fallback(sp, playlist_id, limit=max_tracks)
                if tracks:
                    LOG.info('Recovered %d tracks via web-fallback after API failure', len(tracks))
                else:
                    LOG.error('Failed to recover playlist %s via web-fallback after API failure', playlist_id)
                    return []
            except Exception as e2:
                LOG.error('Web-fallback also failed for %s: %s', playlist_id, e2)
                return []
        else:
            # If playlist() succeeded but tracks failed, re-raise to surface the error
            raise
    # If we got no tracks from API, try a web fallback for public playlists
    if not tracks:
        try:
            tracks = fetch_playlist_tracks_web_fallback(sp, playlist_id, limit=max_tracks)
            if tracks:
                LOG.info('Recovered %d tracks via web-fallback', len(tracks))
        except Exception as e:
            LOG.debug('Web-fallback failed: %s', e)

    LOG.info('Fetched %d tracks from Spotify playlist %s', len(tracks), playlist_id)

    rows = []
    track_titles = []
    for idx, track in enumerate(tracks, 1):
        IDs = []
        with open('CSV.txt', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                IDs.append(row[0])
            track_titles.append(track.get('name'))
        if track.get('id') in IDs:
            LOG.info('Skipping already processed track %s', track.get('name'))
            # be cool
            time.sleep(0.05)
            


        else:
            query = build_query(track)
            total = len(tracks) if tracks else 0
            LOG.info('[%d/%d] Searching: %s', idx, total, query)
            entry = None
            try:
                entry = search_youtube(query)
            except Exception as e:
                LOG.debug('Search error for %s: %s', query, e)
            if entry:
                video_id = entry.get('id')
                video_title = entry.get('title')
                video_url = entry.get('webpage_url') or (f'https://www.youtube.com/watch?v={video_id}' if video_id else None)
            else:
                video_id = None
                video_title = None
                video_url = None
            rows.append({
                'spotify_track_id': track.get('id'),
                'spotify_title': track.get('name'),
                'spotify_artists': ', '.join([a.get('name') for a in track.get('artists', [])]),
                'spotify_duration_ms': track.get('duration_ms'),
                'youtube_video_id': video_id,
                'youtube_title': video_title,
                'youtube_url': video_url,
            })
            # be polite
            time.sleep(0.5)

    if dry_run:
        LOG.info('Dry-run complete; not writing CSV. Found %d mappings.', sum(1 for r in rows if r['youtube_url']))
        return rows

    # write csv

    file_exists = os.path.exists(out_path)
    with open(out_path, 'a', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['spotify_track_id','spotify_title','spotify_artists','spotify_duration_ms','youtube_video_id','youtube_title','youtube_url'])
        if file_exists:
            LOG.info('Appending to existing CSV %s', out_path)
        else:
            LOG.info('Creating new CSV %s', out_path)
            writer.writeheader()
        for r in rows:
            writer.writerow(r)


    
    #write to playlist_csv.txt
    playlists = []   
    if playlist_name:
        with open(out_path_playlist, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    playlists.append(row[0])
        with open(out_path_playlist, 'a', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=['playlist_id', 'playlist_name' ,'track_titles'])
            if os.path.exists(out_path_playlist):
                LOG.info('Appending to existing playlist CSV %s', out_path_playlist)
            else:
                LOG.info('Creating new playlist CSV %s', out_path_playlist)
                writer.writeheader()

            playlist_data = {
                'playlist_id': playlist_id,
                'playlist_name': playlist_name,
                'track_titles': str(track_titles)
            }
            if playlist_id in playlists:
                LOG.info('Playlist %s already recorded in %s, skipping write.', playlist_id, out_path_playlist)
            else:
                LOG.info('Writing playlist data for %s', playlist_id)
                writer.writerow(playlist_data)

        LOG.info('Succesfully wrote CSV to %s!', out_path)
    else:
        LOG.info('No playlist_id aquired; skipping playlist CSV write.')
    return rows


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Map Spotify playlist tracks to YouTube URLs using yt-dlp search')
    parser.add_argument('--playlist', required=True, help='Spotify playlist id (or uri)')
    parser.add_argument('--playlist-name', required=True, help='Spotify playlist friendly name')
    parser.add_argument('--out', default='CSV.txt', help='Output CSV path')
    parser.add_argument('--max-tracks', type=int, default=0, help='Max tracks to process (0 = all)')
    parser.add_argument('--dry-run', action='store_true', help="Don't write CSV; just run searches")
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(message)s')

    max_tracks = args.max_tracks or None
    playlist_name = args.playlist_name
    playlist_id = extract_playlist_id(args.playlist)
    if playlist_id != args.playlist:
        LOG.debug('Extracted playlist id: %s', playlist_id)
    spotify_playlist_to_csv(playlist_id, playlist_name, args.out, 'playlist_CSV.txt', max_tracks=max_tracks, dry_run=args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
