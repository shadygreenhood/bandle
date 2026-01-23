#!/usr/bin/env bash
# loop_mp3s.sh
# Loops over all MP3 files in a folder

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FOLDER=$PROJECT_DIR"/mp3s"  # Default to current directory if no folder provided

if [ -n "$1" ]; then
    FOLDER="$1"
fi

for file in "$FOLDER"/*.mp3; do
    # Check if any mp3 files exist
    [ -e "$file" ] || { echo "No MP3 files found in $FOLDER"; break; }

    echo "Found MP3: $file"
    filename=$(basename "$file")
    folder_name="${filename%.mp3}"
    if [ -e "separated/htdemucs_6s/$folder_name/vocals.wav" ]; then
        echo "Already processed, skipping: $file"
        continue
    else
        echo "Processing: $file"
        
        "$PROJECT_DIR/.venv/bin/python" -m demucs -n htdemucs_6s $file
    fi
done

