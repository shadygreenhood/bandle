from constants import *


import audio_helper

import json
import hashlib
import os
            

import subprocess
from pathlib import Path

logger.debug("loading requests")
import requests                             # type: ignore
logger.debug("loading get_model (demucs)")
from demucs.pretrained import get_model     # type: ignore
logger.debug("loading apply_model (demucs)")
from demucs.apply import apply_model        # type: ignore
logger.debug("loading soundfile")
import soundfile as sf                      # type: ignore
logger.debug("loading yt_dlp")
import yt_dlp                               # type: ignore
logger.debug("loading SpotifyClient")
from  spotify_scraper import SpotifyClient  # type: ignore
logger.debug("loading torch")
import torch                                # type: ignore


# ╭-----------------------------------------------------------------------------------------╮
# |      ╭==╮  ╭==╮  ╭╮ ╮  .  ╭==╮  .  ╭==╮  ╭=-       ╭==╮  ╭==╮  ╭==╮  .  ╭╮ ╮  ╭==╮      |
# |      ╰--╮  ╞--╡  |╰╮|  |   ||   |   .'   ╞-        ╰--╮   ||   ╞=:╯  |  |╰╮|  |  ╮      |
# |      ╰==╯  ╰  ╯  ╰ ╰╯  ╯   ╰╯   ╯  ╰==╯  ╰=-       ╰==╯   ╰╯   ╰  ╰  ╯  ╰ ╰╯  ╰==╯      |
# ╰-----------------------------------------------------------------------------------------╯
def santize_string(str, use="", data=""):
    new_str = ""
    for i in str:
        if not i.lower() in DISALLOWED_CHARS_IN_SANITIZED_TEXT:
            new_str += i

    if new_str == "":
        if use == "print":
            new_str = "song"
        elif use == "artist":
            new_str = "unknown_artist"
        elif use == "song":
            new_str = "unknown_song"
    
    if use == "song":
        temp_data = new_str + "".join(data)
        temp_hash = hashlib.sha1(temp_data.encode("utf-8")).hexdigest()[:8]
        new_str += "_" + temp_hash
    
    if str != new_str:
        logger.debug(f"sanitized: \"{str}\" to \"{new_str}\"")
    return new_str


# ╭---------------------------------------------------------------------------╮
# |      ╭==╮  ╭-.   ╭-.        ╭==╮  ╭    ╭==╮  ╮ ╭  ╭    .  ╭==╮  ╭==╮      |
# |      ╞--╡  |  |  |  |       ╞==╯  |    ╞--╡  ╰╮╯  |    |  ╰--╮   ||       |
# |      ╰  ╯  ╰='   ╰='        ╰     ╰-╯  ╰  ╯   ╯   ╰-╯  ╯  ╰==╯   ╰╯       |
# ╰---------------------------------------------------------------------------╯
def add_playlist():
    logger.pretty_text("\n    > paste the spotify url you want to add (s for skip):\n", style="magenta")
    playlist_url = input("")


    # adding playlist to playlists.json
    if playlist_url != "s" and playlist_url != "":



        if "?" in playlist_url:
            playlist_url = playlist_url.split("?")[0]

        # check if link works.
        try:
            # Use HEAD for efficiency or GET if content validation is needed
            response = requests.head(playlist_url, timeout=5, allow_redirects=True)
            
            # Status codes < 400 generally indicate success
            if response.status_code < 400:
                logger.debug("playlist seems to be available")
            else:
                logger.error("playlist seems to be unavailable, are you sure this is a public playlist?")
                return "error"
        except requests.exceptions.RequestException as e:
            logger.error(f"playlist seems to be unavailable, and failed with this error code: \n{e}\n\n Are you sure you made the playlist public?")
            return "error"


        logger.debug(f"adding {playlist_url} to playlists.json")

        url_type =  "album" if "album" in playlist_url else "playlist" if "playlist" in playlist_url else "unknown"
        if url_type == "unknown":
            logger.error("\n    the url provided doesnt seem to be neither a playlist nor an album, aborting\n")
            raise Exception("\n    the url provided doesnt seem to be neither a playlist nor an album, aborting\n")
        logger.debug(f"detected url to be a {url_type} url")

        client = SpotifyClient()

        logger.debug("extracting {}")
        if url_type == "playlist":
            buffer_dir_contents = client.get_playlist_info(playlist_url)
        elif url_type == "album":
            buffer_dir_contents = client.get_album_info(playlist_url)
        
        logger.debug(f"adding {url_type}: id: \"{buffer_dir_contents['id']}\" name: \"{santize_string(buffer_dir_contents['name'], use='print')}\"")

        tracks = buffer_dir_contents["tracks"]
        data = []
        for track in tracks:
            if url_type == "playlist":
                artists = track["artists"]
            elif url_type == "album":
                artists = buffer_dir_contents["artists"]

            split = [artists[0]["name"]]
            if len(artists) == 1: # weird issue with spotifyscraper where all artists are concatenated in a string instead of seperate list elements
                if "," in artists[0]["name"]:
                    split = artists[0]["name"].split(",\xa0")
            artists = [santize_string(i, use="artist") for i in split]

            data.append({
                "name": santize_string(track["name"], use="song", data=artists),
                "artists": artists
            })


        with open(PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
            playlists_json_dir_contents = json.load(f)

        playlists_json_dir_contents[buffer_dir_contents["id"]] = {
            "name": buffer_dir_contents["name"], 
            "data": data
            }

        with open(PLAYLIST_JSON_DIR, "w", encoding="utf-8") as f:
            json.dump(playlists_json_dir_contents, f, indent=4, ensure_ascii=False)


    # ensuring all songs are in songs.json
    logger.debug("updating songs.json accordingly")
    with open(PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
        playlists_json_dir_contents = json.load(f)
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
        SONGS_DIR_contents = json.load(f)

    for i in playlists_json_dir_contents:
        for j in playlists_json_dir_contents[i]:
            if j == "data":
                for k in playlists_json_dir_contents[i][j]:
                    if not k["name"] in SONGS_DIR_contents:
                        SONGS_DIR_contents[k["name"]] = {"status": "new", "artists": k["artists"]}

    # baking names of artists into a better format for data parsing
    logger.debug("preprocessing artist data")
    for i in SONGS_DIR_contents.keys():
        SONGS_DIR_contents[i]["baked_artists"] = " ".join([x.lower() for x in SONGS_DIR_contents[i]["artists"]])

    with open(SONGS_JSON_DIR, 'w', encoding="utf-8") as f:
        json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)


# ╭--------------------------------------------------------------------------------------------╮
# |      ╭-.   ╭==╮  ╭  ╮  ╭╮ ╮  ╭    ╭==╮  ╭==╮  ╭-.        ╭==╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      |  |  |  |  |╭╮|  |╰╮|  |    |  |  ╞--╡  |  |       ╰--╮  |  |  |╰╮|  |  ╮  ╰--╮      |
# |      ╰='   ╰==╯  ╰╯╰╯  ╰ ╰╯  ╰-╯  ╰==╯  ╰  ╯  ╰='        ╰==╯  ╰==╯  ╰ ╰╯  ╰==╯  ╰==╯      |
# ╰--------------------------------------------------------------------------------------------╯


def download_songs(songs_to_download, silent=False, give_status=False, url=""):
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
        SONGS_DIR_contents = json.load(f)

    
    if songs_to_download != []:
        if not silent:
            logger.pretty_text(f"downloading {len(songs_to_download)} missing songs", "magenta")
    else:
        if not silent:
            logger.pretty_text("lucky you: there's nothing to download!", "magenta")

    for i in range(len(songs_to_download)):
        
        title = songs_to_download[i]
        if SONGS_DIR_contents[title]["status"] == "new":

            artists = SONGS_DIR_contents[songs_to_download[i]]["artists"]
            query = f"{''.join(title.split('_')[:-1])} {' '.join(artists)} audio"
            folder_end = (title+".%(ext)s")
            if getattr(sys, 'frozen', False):
                ydl_opts = {
                "format": "bestaudio/best",
                    "ffmpeg_location": str(FFMPEG_DIR),
                    "outtmpl": str(RAW_TRACK_AUDIO_DIR / folder_end),
                    "quiet": True,
                    "no_warnings": True, 
                    "logger": YTDLPLogger(), 
                    "match_filter": duration_filter, # less than 10 minutes
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "wav",
                    }],
                }
            else:
                ydl_opts = {
                "format": "bestaudio/best",
                    "outtmpl": str(RAW_TRACK_AUDIO_DIR / folder_end),
                    "quiet": True,
                    "no_warnings": True, 
                    "logger": YTDLPLogger(), 
                    "match_filter": duration_filter, # less than 10 minutes
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "wav",
                    }],
                }
            if not url == "":
                folder_end = (title+".wav")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download(url)
                if not Path(PROJECT_DIR / "raw_track_audio" /  folder_end).exists():
                    logger.debug(f'checked path: {str(Path(PROJECT_DIR / "raw_track_audio" /  folder_end))}')
                    logger.error("there was an error while downloading the audio")
                    return "error"
                else:
                    logger.pretty_text("audio downloaded successfully!", "magenta bold")
            else:
                if not silent: 
                    logger.pretty_text(f"[{i+1}/{len(songs_to_download)}] dowloading from query: \"{query}\"", "magenta")
                else:
                    logger.pretty_text(f"dowloading from query: \"{query}\"", "magenta")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"ytsearch1:{query}"])
                folder_end = title+".wav"
                if not Path(PROJECT_DIR / "raw_track_audio" /  folder_end).exists():
                    while True:
                        logger.error("yt-dlp had issues downloading your track\n" \
                                    "this may be due to several things:\n" \
                                    "  - bad internet, or a firewall or some sorts\n" \
                                    "  - yt-dlp did not find relevant results while\n" \
                                    "    looking up the displayed query\n" \
                                    "\n" \
                                    "for further troubleshooting, please look up your\n" \
                                    "song's youtube video and paste its url here")
                        yt_url = input(">")
                        if yt_url == "q":
                            return "error"
                        logger.debug("temporarily disabling pretty printing for more practical logs")
                        debug_ydl_opts = ydl_opts
                        debug_ydl_opts["quiet"] = False
                        debug_ydl_opts["no_warinings"] = False
                        debug_ydl_opts["logger"] = None
                        with yt_dlp.YoutubeDL(debug_ydl_opts) as ydl:
                            ydl.download(yt_url)
                        if Path(PROJECT_DIR / "raw_track_audio" /  folder_end).exists():
                            logger.pretty_text("Yippe! This worked!", "magenta bold")
                            SONGS_DIR_contents[title]["status"] = "downloaded"
                            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
                            break
                        else:
                            logger.error("This didnt solve the issue...\n   try again? \[y/n]")
                            if not input() == "y":
                                break
                
                else:
                    SONGS_DIR_contents[title]["status"] = "downloaded"
                    with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                        json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
    if give_status:
        return SONGS_DIR_contents[title]["status"]
# ╭-----------------------------------------------------------------------------╮
# |      ╭==╮  ╭==╮  ╭    .  ╭==╮       ╭==╮  ╭==╮  ╭==╮  ╭=-╮  ╭  ╭  ╭==╮      |
# |      ╰--╮  ╞==╯  |    |   ||         ||   ╞=:╯  ╞--╡  |     ╞=:   ╰--╮      |
# |      ╰==╯  ╰     ╰-╯  ╯   ╰╯         ╰╯   ╰  ╰  ╰  ╯  ╰=-╯  ╰  ╰  ╰==╯      |
# ╰-----------------------------------------------------------------------------╯
from rich.live import Live
def split_tracks(songs_to_split, silent=False, give_status=False):
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
        SONGS_DIR_contents = json.load(f)
 
    if len(songs_to_split) == 0:
        if not silent:
            logger.pretty_text("lucky you: there's no audio to split!", "magenta")
    else:
        if not silent:
            logger.pretty_text(f"splitting {len(songs_to_split)} tracks, this might take a while...", "magenta bold")
        skip = False
        for i in range(len(songs_to_split)):
            title = songs_to_split[i]
            folder_end = title + ".wav"
            if not silent:
                logger.pretty_text(f"[{i+1}/{len(songs_to_split)}] splitting track: \"{title[:-9]}\"", "magenta")

            if Path(STEMS_FOLDER / title).exists():
                logger.warning("there seems to already be a folder for the seperated audio files, do you want to:\n \[o]: overwrite them\n \[s]: skip seperation?\n \[a]: skip all ambiguous cases")
                if not skip == "all":
                    skip = False
                    while True:
                        opt4 = input(">")
                        if opt4 in ["s", "o", "q", "a"]:
                            if opt4 == "q":
                                return "error"
                            if opt4 == "s":
                                skip = True
                                break
                            if opt4 == "o":
                                break
                            if opt4 == "a":
                                skip = "all"
                                break
                        else:
                            logger.error("answer needs to be s for skip, or o for overwrite")
                if skip == False:
                    # loading song and model
                    wav, sr = sf.read(RAW_TRACK_AUDIO_DIR / folder_end)
                    wav = torch.tensor(wav, dtype=torch.float32).T
                    if wav.shape[0] == 1:
                        wav = wav.repeat(2, 1)
                    wav = wav / wav.abs().max()
                    wav = wav.unsqueeze(0)
                    model = get_model("htdemucs_6s")
                    model.cpu()

                    # run seperation with process hook
                    with Live("", refresh_per_second=10) as live:
                        progress_capture = ProgressCapture(live)
                        with torch.no_grad():
                            # redirect Demucs tqdm output (stderr) to our capture
                            import contextlib
                            with contextlib.redirect_stderr(progress_capture):
                                sources = apply_model(model, wav, device="cpu", progress=True)
                    sources = sources[0]

                    # save output
                    os.makedirs(STEMS_FOLDER / title, exist_ok=True)
                    for j, stem in enumerate(model.sources):
                        out_path = os.path.join(STEMS_FOLDER / title, f"{stem}.wav")
                        sf.write(out_path, sources[j].T.numpy(), sr)

                    # check if files are actually here before proceding
                    if Path(STEMS_FOLDER / title).exists():
                        if not silent:
                            logger.pretty_text(f"[{i+1}/{len(songs_to_split)}] successfully split the track: {title[:-9]}", "magenta")
                        else:
                            logger.debug(f"successfully split the track: {title[:-9]}")
                        logger.debug("converting back to wavs for easier processing")

                        # converting to wavs
                        failure = False
                        for mp3_file in Path(STEMS_FOLDER / title).rglob("*.mp3"):
                            wav_file = mp3_file.with_suffix(".wav")
                            result = subprocess.run(
                                ["ffmpeg", "-loglevel", "error", "-i", str(mp3_file), str(wav_file)]
                            )
                            if result.returncode == 0:
                                mp3_file.unlink()  # delete original
                            else:
                                failure = True
                        
                        if not failure: # check for faliure converting to wavs very unlikely
                            folder_end = title + ".wav"
                            logger.debug(f"removing now useless audio: \"{RAW_TRACK_AUDIO_DIR / folder_end}\"")
                            SONGS_DIR_contents[title]["status"] = "split"
                            Path(RAW_TRACK_AUDIO_DIR / folder_end).unlink()
                            # recording that
                            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
                            
                        else:
                            logger.error("something went wrong")
                    else:
                        logger.error("did not split")
                else:
                    SONGS_DIR_contents[title]["status"] = "split"
                    if Path(RAW_TRACK_AUDIO_DIR / folder_end).exists():
                        Path(RAW_TRACK_AUDIO_DIR / folder_end).unlink()
                    with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
    if give_status:
        return SONGS_DIR_contents[title]["status"]

# ╭------------------------------------------------------------------------------------------╮
# |      ╭==╮  ╭╮ ╮  ╭==╮  ╭    ╮ ╭  ╭==╮  ╭=-       ╭==╮  ╭==╮  ╭==╮  ╭=-╮  ╭  ╭  ╭==╮      |
# |      ╞--╡  |╰╮|  ╞--╡  |    ╰╮╯  ╰--╮  ╞-         ||   ╞=:╯  ╞--╡  |     ╞=:   ╰--╮      |
# |      ╰  ╯  ╰ ╰╯  ╰  ╯  ╰-╯   ╯   ╰==╯  ╰=-        ╰╯   ╰  ╰  ╰  ╯  ╰=-╯  ╰  ╰  ╰==╯      |
# ╰------------------------------------------------------------------------------------------╯
def analyse_tracks(songs_to_analyse, silent=False, give_status=False):
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
            SONGS_DIR_contents = json.load(f)

    if len(songs_to_analyse) == 0:
        if not silent:
            logger.pretty_text("lucky you: there are no songs to analyse!", "magenta")
    else:
        if not silent:
            logger.pretty_text(f"analysing {len(songs_to_analyse)} songs...", "magenta")

        analyser = audio_helper.Player_obj(STEMS, STEMS_FOLDER, volume=70)

        for i in songs_to_analyse:
            analyser.load(i)
            compressed_diag = analyser.analysing_pipeline()
            SONGS_DIR_contents[i]["baked_diagnosis"] = compressed_diag
            SONGS_DIR_contents[i]["status"] = "analysed"
            if not silent:
                logger.pretty_text(f"[{songs_to_analyse.index(i) + 1}/{len(songs_to_analyse)}] analysed {i[:-9]}", "magenta")
            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
    if give_status:
        return SONGS_DIR_contents[i]["status"]

# ╭-------------------------------------------------------------------------------╮
# |      ╭==╮  ╭=-  ╭==╮  ╭=-  ╭==╮       ╭==╮  ╭==╮  ╭==╮  ╭=-╮  ╭  ╭  ╭==╮      |
# |      ╞=:╯  ╞-   ╰--╮  ╞-    ||         ||   ╞=:╯  ╞--╡  |     ╞=:   ╰--╮      |
# |      ╰  ╰  ╰=-  ╰==╯  ╰=-   ╰╯         ╰╯   ╰  ╰  ╰  ╯  ╰=-╯  ╰  ╰  ╰==╯      |
# ╰-------------------------------------------------------------------------------╯

def reset_tracks(songs_to_analyse, silent=False, give_status=False):
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
            SONGS_DIR_contents = json.load(f)

    if len(songs_to_analyse) == 0:
        if not silent:
            logger.pretty_text("lucky you: there are no songs to reset!", "magenta") # unused
    else:
        if not silent:
            logger.pretty_text(f"resetting {len(songs_to_analyse)} songs...", "magenta")

        for i in songs_to_analyse:

            if "baked_didagnosis" in SONGS_DIR_contents.keys():
                SONGS_DIR_contents[i].pop("baked_diagnosis")
            SONGS_DIR_contents[i]["status"] = "new"
            if Path(RAW_TRACK_AUDIO_DIR / (i+".wav")).exists():
                Path(RAW_TRACK_AUDIO_DIR / (i+".wav")).unlink()
            if Path(STEMS_FOLDER / (i)).exists():
                for file in Path(STEMS_FOLDER / (i)).iterdir():
                    file.unlink()
                Path(STEMS_FOLDER / (i)).rmdir()

            if not silent:
                logger.pretty_text(f"[{songs_to_analyse.index(i) + 1}/{len(songs_to_analyse)}] reset {i[:-9]}", "magenta")
            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
    if give_status:
        return SONGS_DIR_contents[i]["status"]
    