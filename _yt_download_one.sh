#!/usr/bin/env bash
# _yt_download_one.sh
# Download a single YouTube URL to MP3 with a fallback if a requested format isn't available.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <url> <outdir>" >&2
  exit 2
fi

URL="$1"
OUTDIR="$2"



# Preferred command (specify bestaudio to prefer audio-only streams)
PREFERRED=(yt-dlp --newline --no-playlist -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "$OUTDIR/%(title).200s - %(id)s.%(ext)s" "$URL")
# Fallback: don't force format, let yt-dlp pick what it can
FALLBACK=(yt-dlp --newline --no-playlist --extract-audio --audio-format mp3 --audio-quality 0 -o "$OUTDIR/%(title).200s - %(id)s.%(ext)s" "$URL")

# Run preferred, if fails try fallback and record failures
if "${PREFERRED[@]}"; then
  exit 0
else
  echo "Primary download failed for $URL; attempting fallback..." >&2
  if "${FALLBACK[@]}"; then
    exit 0
  else
    echo "Fallback also failed for $URL" >&2
    mkdir -p "$OUTDIR"
    echo "$URL" >> "$OUTDIR/failed_downloads.txt"
    exit 1
  fi
fi
