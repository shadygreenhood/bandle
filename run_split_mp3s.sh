#!/usr/bin/env bash
# Wrapper to run split_mp3s.py with sane defaults, logging, and summary
# Usage: ./run_split_mp3s.sh [options]

set -euo pipefail

print_usage() {
  cat <<-USAGE
  Usage: $0 [options]

  Options:
    -i DIR    Input directory (default: mp3s)
    -o DIR    Output directory (default: stems_final)
    -s N      Number of stems for spleeter (2,4,5) (default: 4)
    -c CODEC  Output codec (wav|mp3) (default: mp3)
    -n N      Concurrency (default: 1)
    -d        Dry-run (do not run separation)
    -l FILE   Log filename (default: split-<timestamp>.log)
      -p        Show live progress while running (polls output directory)
    -h        Show this help

  Example:
    ./run_split_mp3s.sh -i mp3s -o stems_final -s 4 -c mp3 -n 1

USAGE
}

# defaults
INDIR="mp3s_2"
OUTDIR="stems_final_2"
STEMS=5
CODEC="mp3"
CONCURRENCY=4
DRY_RUN=0
LOG="split-$(date +%Y%m%d-%H%M%S).log"
PROGRESS=0
CMD_PID=0
TAIL_PID=0

# cleanup on signal: kill child and tailer if running
cleanup() {
  if [[ -n "$CMD_PID" && "$CMD_PID" -ne 0 ]]; then
    kill -TERM "$CMD_PID" 2>/dev/null || true
  fi
  if [[ -n "$TAIL_PID" && "$TAIL_PID" -ne 0 ]]; then
    kill -TERM "$TAIL_PID" 2>/dev/null || true
  fi
}
trap 'cleanup; exit 130' INT TERM

while getopts ":i:o:s:c:n:l:pdh" opt; do
  case "$opt" in
    i) INDIR="$OPTARG" ;; 
    o) OUTDIR="$OPTARG" ;; 
    s) STEMS="$OPTARG" ;; 
    c) CODEC="$OPTARG" ;; 
    n) CONCURRENCY="$OPTARG" ;; 
    p) PROGRESS=1 ;; 
    l) LOG="$OPTARG" ;; 
    d) DRY_RUN=1 ;; 
    h) print_usage; exit 0 ;; 
    \?) echo "Unknown option: -$OPTARG" >&2; print_usage; exit 2 ;;
    :) echo "Missing arg for -$OPTARG" >&2; print_usage; exit 2 ;;
  esac
done

# Find python in .venv if present
if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "No python3 binary found and .venv/bin/python missing. Install Python or create .venv." >&2
  exit 3
fi

echo "Using Python: $PYTHON"

echo "Validating Python script (syntax check)..."
# continue on syntax error but show it
$PYTHON -m py_compile split_mp3s.py || true
CMD=("$PYTHON" "split_mp3s.py" "--indir" "$INDIR" "--outdir" "$OUTDIR" "--stems" "$STEMS" "--concurrency" "$CONCURRENCY" "--codec" "$CODEC")
if [[ $DRY_RUN -eq 1 ]]; then
  CMD+=("--dry-run")
else
  CMD+=("--overwrite")
fi

# create outdir parent if not exists so logs have somewhere to go
mkdir -p "$OUTDIR"

echo "Running: ${CMD[*]}"

# helper: compute inputs
INPUT_COUNT=0
if [[ -d "$INDIR" ]]; then
  INPUT_COUNT=$(find "$INDIR" -type f -name '*.mp3' | wc -l)
fi

print_progress() {
  local count pct bar width filled
  width=40
  if [[ $INPUT_COUNT -eq 0 ]]; then
    printf "Progress: no inputs found\n"
    return
  fi
  # count distinct subdirs that have at least one mp3
  count=$(find "$OUTDIR" -type f -name '*.mp3' -printf '%h\n' 2>/dev/null | sort -u | wc -l)
  pct=$(( 100 * count / INPUT_COUNT ))
  filled=$(( width * count / INPUT_COUNT ))
  bar=$(printf '%0.s#' $(seq 1 $filled); printf '%0.s-' $(seq 1 $((width-filled))))
  printf '\rProgress: [%s] %d%% (%d/%d) ' "$bar" "$pct" "$count" "$INPUT_COUNT"
}

# run with optional live progress
if [[ ${PROGRESS:-0} -eq 1 ]]; then
  # run the command redirecting stdout/stderr to the log in background
  ( "${CMD[@]}" ) >"$LOG" 2>&1 &
  CMD_PID=$!
  # tail the log so user sees output live
  tail -n +1 -f "$LOG" &
  TAIL_PID=$!
  # print periodic progress lines while the command runs
  while kill -0 $CMD_PID 2>/dev/null; do
    print_progress
    sleep 2
  done
  # final progress and wait
  wait $CMD_PID || true
  EXIT_CODE=$?
  # give final update
  print_progress
  printf '\n'
  kill $TAIL_PID 2>/dev/null || true
else
  # run and tee output (no live progress)
  ( "${CMD[@]}" ) 2>&1 | tee "$LOG"
  EXIT_CODE=${PIPESTATUS[0]:-0}
fi

# summary
echo "--- Run exit code: $EXIT_CODE"
echo "--- MP3 file count in $OUTDIR:"
find "$OUTDIR" -type f -name '*.mp3' | wc -l

# show a sample listing (first output folder)
SAMPLE_DIR=$(find "$OUTDIR" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)
if [[ -n "$SAMPLE_DIR" ]]; then
  echo "--- sample listing: $SAMPLE_DIR"
  ls -la "$SAMPLE_DIR" || true
else
  echo "--- no sample directory found under $OUTDIR"
fi

exit "$EXIT_CODE"
