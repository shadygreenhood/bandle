#!/usr/bin/env bash

# Resolve script directory reliably
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd 2>/dev/null || echo ".")"
VENV_PATH="$SCRIPT_DIR/.venv-1/bin/python"

# Default MP3 folder
FOLDER="$SCRIPT_DIR/mp3s"

# Allow overriding folder and venv path by argument

if [ -n "$1" ]; then
    VENV_PATH="$1"
fi
if [ -n "$2" ]; then
    if [ "$2" != "default" ]; then
        FOLDER="$2"
    fi
fi

echo "MP3 folder: $FOLDER"

# Enable nullglob so *.mp3 expands to nothing if no files exist
shopt -s nullglob

# Loop over MP3 files
for file in "$FOLDER"/*.mp3; do
    [ -e "$file" ] || { echo "No MP3 files found in $FOLDER"; break; }

    echo "Found MP3: $file"

    # Extract filename without path (basename) and remove .mp3 extension
    filename="${file##*/}"          # removes directory path
    folder_name="${filename%.mp3}"  # removes .mp3 extension

    # Check if already processed
    if [ -e "$SCRIPT_DIR/separated/htdemucs_6s/$folder_name/vocals.wav" ]; then
        echo "Already processed, skipping: $file"
        continue
    fi

    echo "Processing: $file"
    
    # Run demucs
    "$SCRIPT_DIR/$VENV_PATH/Scripts/python.exe" -m demucs -n htdemucs_6s "$file"
done
