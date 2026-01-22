#!/usr/bin/env bash
# download_from_csv.sh
#
# Reads a CSV file (default CSV.txt) and downloads YouTube URLs as MP3s using yt-dlp.
# The output MP3s are named using the Spotify title from the second column of the CSV.
#
# Usage:
#   ./download_from_csv.sh --csv CSV.txt --outdir mp3s --dry-run
#
# Notes:
#   - The Spotify title is assumed to be in the SECOND column of the CSV.
#   - The YouTube URL column header defaults to "youtube_url" but will be auto-detected if missing.

set -euo pipefail
IFS=$'\n\t'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CSV_FILE=$PROJECT_DIR+"\\CSV.txt"
OUTDIR=$PROJECT_DIR+"mp3s"
DRY_RUN=0
URL_COL="youtube_url"

print_usage() {
  cat <<EOF
Usage: $0 [--csv FILE] [--outdir DIR] [--dry-run] [--url-col NAME]

Options:
  --csv FILE        Path to CSV file (default: CSV.txt)
  --outdir DIR      Output directory for MP3s (default: mp3s)
  --dry-run         Print commands without executing
  --url-col NAME    CSV header for YouTube URLs (default: youtube_url)
  -h, --help        Show this help and exit
EOF
}

# Parse CLI args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv) CSV_FILE="$2"; shift 2;;
    --outdir) OUTDIR="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    --url-col) URL_COL="$2"; shift 2;;
    -h|--help) print_usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; print_usage; exit 2;;
  esac
done

# Validate dependencies and inputs
if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Error: yt-dlp not found in PATH. Install it first." >&2
  exit 2
fi

if [[ ! -f "$CSV_FILE" ]]; then
  echo "Error: CSV file not found: $CSV_FILE" >&2
  exit 2
fi

mkdir -p "$OUTDIR"

# Create temporary file
TMP_COMBINED=$(mktemp)

# Extract URL + title from CSV (tab-separated)
python3 - "$CSV_FILE" "$URL_COL" "$TMP_COMBINED" <<'PY'
import csv, sys
csv_file, url_col, out_file = sys.argv[1:4]
try:
    with open(csv_file, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        headers = next(reader, [])
        headers = [h.strip() for h in headers]
        try:
            url_idx = headers.index(url_col)
        except ValueError:
            url_idx = next((i for i, h in enumerate(headers) if 'youtube' in h.lower()), None)
        if url_idx is None:
            sys.stderr.write(f"Column '{url_col}' not found in CSV header.\n")
            sys.exit(2)

        with open(out_file, 'w', encoding='utf-8') as out:
            for row in reader:
                if len(row) > max(url_idx, 1):
                    url = row[url_idx].strip()
                    title = row[1].strip()
                    if url and title:
                        out.write(f"{url}\t{title}\n")
except Exception as e:
    sys.stderr.write(str(e) + '\n')
    sys.exit(2)
PY

# Read URL + title, download one by one
while IFS=$'\t' read -r url title; do
  # Sanitize title for filesystem safety
  safe_title=$(echo "$title" | tr '/\\:*?"<>|' '_' | sed 's/[[:space:]]\+/_/g')
  outfile="${OUTDIR}/${safe_title}.mp3"

  if [[ -f "$outfile" ]]; then
    echo "Skipping existing: $title"
    continue
  fi

    echo "Downloading: $title"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[DRY RUN] yt-dlp --no-cache-dir --geo-bypass --force-ipv4 -f 'bestaudio/best' --extract-audio --audio-format mp3 --audio-quality 0 -o \"$outfile\" \"$url\""
  else
    # Retry up to 3 times on failure
    for attempt in {1..3}; do
      if yt-dlp --no-cache-dir --geo-bypass --force-ipv4 \
                -f "bestaudio/best" \
                --extract-audio --audio-format mp3 --audio-quality 0 \
                -o "$outfile" "$url"; then
        success=1
        break
      else
        echo "⚠️  Attempt $attempt failed for: $title"
        success=0
        sleep 2
      fi
    done

    if [[ $success -eq 0 ]]; then
      echo "❌ Failed to download after 3 attempts: $title ($url)" | tee -a "${OUTDIR}/failed_downloads.txt"
    fi
  fi
done < "$TMP_COMBINED"

rm -f "$TMP_COMBINED"

echo "✅ Done. MP3s (if downloaded) are in: $OUTDIR"
