import subprocess
import os
import logging
from time import sleep
from pathlib import Path
import sys
import platform
 



def help(error=""):
    print(f"There was an error while parsing the config.")
    print(str(error))
    print("\n" \
    "this script is the final wrapper for the shadygreenhood bandle project\n" \
    "\n" \
    "Usage: bandle.py\n" \
    "\n" \
    "\n" \
    f"Config default location: {PROJECT_DIR}/config.txt\n" \
    "\n")
    raise Exception(str(error))

#IMPORTANT VARS
if "/" in str(Path(__file__)):
    PROJECT_DIR =  "/".join(str(Path(__file__).resolve().parent).split("/")[:-1])
elif "\\" in str(Path(__file__)):
    PROJECT_DIR =  "\\".join(str(Path(__file__).resolve().parent).split("\\")[:-1])
else:
    raise Exception(f"failed to resolve current project directory with cwd={str(Path(__file__))}")
SCRIPT_DIR = "bandle"
CSV_PATH = f"{PROJECT_DIR}/{SCRIPT_DIR}/CSV.txt"
INTERPRETER_PATH = sys.executable
VERBOSE = False
VERBOSE_FLAG = "--verbose" if VERBOSE else ""
MP3_DATA_DIR = f"{PROJECT_DIR}/mp3s"
SCALE = 0.5
CURR_OS = -1

with open(f"{PROJECT_DIR}/config.txt", "r") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "SCALE" in i:
            if len(i.split("=")) > 0:
                SCALE = i.split("=")[1]
            else:
                help(f"no scale provided in {PROJECT_DIR}/config.txt")
        if "CURR_OS" in i:
            if len(i.split("=")) > 0:
                CURR_OS = i.split("=")[1]
            else:
                help(f"no OS provided in {PROJECT_DIR}/config.txt")

if CURR_OS == -1:
    print("OS not specified in config...")
    CURR_OS = platform.system()
    print(f"{CURR_OS} host has been detected")
    if CURR_OS == "Windows":
        print("running windows script")
    else:
        if CURR_OS == "Linux":
            print("running linux script")
        else:
            print("os not recognised, defaulting to linux script")
            CURR_OS = "Linux"


#TODO: add a flags such as --help, --verbose, etc.
#TODO: add a progress bar for long operations.
#No --dry-run flag, they are only useful for testing, and this script is not for testing.


def main():

    #starting logging
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] - %(levelname)s - %(message)s")

    # Ensure env vars are defined
    logging.info("Setting up environment variables for Spotify API access...")
    required_env_vars = os.environ.copy()
    required_env_vars["SPOTIFY_CLIENT_ID"] = "##REMOVED_SPOTIFY_CLIENT_ID"
    required_env_vars["SPOTIFY_CLIENT_SECRET"] = "##REMOVED_SPOTIFY_CLIENT_SECRET"
    required_env_vars["SPOTIFY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"

    # Run spotify_to_youtube.py
    playlist_url = input("Enter Spotify Playlist URL: [s for skip] ")
    if playlist_url.lower() == 's':
        logging.info("Skipping Spotify to YouTube conversion as per user request.")
        sleep(1)
    else:
        input_name = input("Enter a friendly name for the playlist: ")
        logging.info("Converting Spotify playlist to YouTube URLs in 3...")
        sleep(1)
        logging.info("Converting Spotify playlist to YouTube URLs in 2...")
        sleep(1)
        logging.info("Converting Spotify playlist to YouTube URLs in 1...")
        sleep(1)
        cmd = f"\"{INTERPRETER_PATH} {PROJECT_DIR}/{SCRIPT_DIR}/spotify_to_youtube.py\" --playlist \"{playlist_url}\" --playlist-name \"{input_name}\" --max-tracks 0  --out \"{CSV_PATH}\" {VERBOSE_FLAG}"
        subprocess.run(cmd, shell=True, env=required_env_vars)

    # Run download_from_csv.sh
    logging.info("Downloading MP3s from YouTube URLs in CSV in 3...")
    sleep(1)
    logging.info("Downloading MP3s from YouTube URLs in CSV in 2...")
    sleep(1)
    logging.info("Downloading MP3s from YouTube URLs in CSV in 1...")
    sleep(1)
    logging.info("Starting download...")
    cmd = f"\"{PROJECT_DIR}/{SCRIPT_DIR}/download_from_csv.sh\" --csv \"{CSV_PATH}\" --outdir \"{MP3_DATA_DIR}\" --url-col \"youtube_url\""
    subprocess.run(cmd, shell=True)

    logging.info("They are done downloading!")
    sleep(1)
    logging.info("Starting separation of MP3s in 3...")
    sleep(1)
    logging.info("Starting separation of MP3s in 2...")
    sleep(1)
    logging.info("Starting separation of MP3s in 1...")
    sleep(1)
    logging.info("Starting separation now...")
    print(MP3_DATA_DIR)
    cmd = f"\"{PROJECT_DIR}/{SCRIPT_DIR}/final_split_tool.sh\" \"{MP3_DATA_DIR}\""
    subprocess.run(cmd, shell=True)

    logging.info("All tasks completed successfully!")
    sleep(3)
    logging.info("Opening bandle mixer...")
    sleep(1)
    cmd = f"\"{INTERPRETER_PATH}\" \"{PROJECT_DIR}/{SCRIPT_DIR}/mixer2.py\" --scale={SCALE}"
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()

