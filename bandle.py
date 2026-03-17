import subprocess
from pathlib import Path
import json
import yt_dlp           # type: ignore
from time import sleep

import audio_helper

from constants import *



#overriding constants with config
with open(PROJECT_DIR / "config.txt", "r") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "SCALE" in i:
            if len(i.split("=")) > 0:
                CF_SCALE = i.split("=")[1]
            else:
                help(f"no scale provided in {CONFIG_DIR}")
        if "CURR_OS" in i:
            if len(i.split("=")) > 0:
                CURR_OS = i.split("=")[1]
            else:
                help(f"no OS provided in {CONFIG_DIR}")
        if "WEAK_INTERNET" in i:
            if len(i.split("=")) > 0:
                try:
                    WEAK_INTERNET = False if i.split("=")[1] == "False" else True if i.split("=")[1] == "True" else WEAK_INTERNET
                except:
                    help(f"failed to convert" + str(i.split("=")[1]) + "to a bool")
            else:
                help(f"no OS provided in {CONFIG_DIR}")
        if "SKIP_SPLIT" in i:
            if len(i.split("=")) > 0:
                try:
                    SKIP_SPLIT = False if i.split("=")[1] == "False" else True if i.split("=")[1] == "True" else SKIP_SPLIT
                except:
                    help(f"failed to convert" + str(i.split("=")[1]) + "to a bool")
            else:
                help(f"no OS provided in {CONFIG_DIR}")

# filtering possible OSes
if CURR_OS == "Windows":
    print("running windows script")
else:
    if CURR_OS == "Linux":
        print("running linux script")
    else:
        print("os not recognised, defaulting to linux script")
        CURR_OS = "Linux"

# init vars
playlist_url = input("paste the spotify url you want to add (s for skip):  ")


def santize_string(str):
    new_str = ""
    for i in str:
        if i.lower() in ALLOWED_CHARS_IN_SANITIZED_TEXT:
            new_str += i
    if new_str == "":
        new_str = "FAILED TO SANITIZE"
    if str != new_str:
        print(f"sanitized: {str} to {new_str}")
    return new_str


# adding playlist to playlists.json
if playlist_url != "s" and playlist_url != "":

    # ensuring buffer isnt contaminated
    with open(BUFFER_DIR, "w") as f:
        f.write("")

    album =  True if "album" in playlist_url else False
    cmd = [
        "spotify-scraper",
        "playlist" if not album else "album",
        playlist_url,
        "--output",
        BUFFER_DIR
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Spotify scraper failed, likely non fatal though, continuing...")
        print("Error: ", e)
        print("Exit code:", e.returncode)

    with open(BUFFER_DIR, "r", encoding="utf-8") as f:
        buffer_dir_contents = json.load(f)

    print("adding playlist: id: " + buffer_dir_contents["id"] + " name: " + santize_string(buffer_dir_contents["name"]))

    tracks = buffer_dir_contents["tracks"]

    data = []
    for track in tracks:

        if not album:
            artists = track["artists"]
        else:
            artists = buffer_dir_contents["artists"]

        split = [artists[0]["name"]]
        if len(artists) == 1:
            if "," in artists[0]["name"]:
                split = artists[0]["name"].split(",\xa0")
        artists = [santize_string(i) for i in split]
        
        data.append({
            "name": santize_string(track["name"]),
            "artists": artists
        })

    try:
        with open(PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
            playlists_json_dir_contents = json.load(f)
    except:
        playlists_json_dir_contents = {}


    playlists_json_dir_contents[buffer_dir_contents["id"]] = {
        "name": buffer_dir_contents["name"], 
        "data": data
        }

    with open(PLAYLIST_JSON_DIR, "w", encoding="utf-8") as f:
        json.dump(playlists_json_dir_contents, f, indent=4, ensure_ascii=False)


# ensuring all songs are in songs.json
with open(PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
    playlists_json_dir_contents = json.load(f)

try:
    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
        SONGS_DIR_contents = json.load(f)
except:
    SONGS_DIR_contents = {}

for i in playlists_json_dir_contents:
    for j in playlists_json_dir_contents[i]:
        if j == "data":
            for k in playlists_json_dir_contents[i][j]:
                if not k["name"] in SONGS_DIR_contents:
                    SONGS_DIR_contents[k["name"]] = {"status": "new", "artists": k["artists"]}

# baking names of artists into a better format for data parsing
for i in SONGS_DIR_contents.keys():
    SONGS_DIR_contents[i]["baked_artists"] = " ".join([x.lower() for x in SONGS_DIR_contents[i]["artists"]])

with open(SONGS_JSON_DIR, 'w', encoding="utf-8") as f:
    json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)



#dowloading missing songs
if not WEAK_INTERNET:
    class YTDLPLogger:
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(f"[ERROR] {msg}")

    songs_to_download = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == "new"]
    if songs_to_download != []:
        print(f"downloading {len(songs_to_download)} missing songs")
    else:
        print("lucky you: there's nothing to download!")
    for i in range(len(songs_to_download)):
        
        title = songs_to_download[i]
        if SONGS_DIR_contents[title]["status"] == "new":

            artists = SONGS_DIR_contents[songs_to_download[i]]["artists"]
            query = f"{title} {' '.join(artists)} audio"
            folder_end = (title+".%(ext)s")
            ydl_opts = {
            "format": "bestaudio/best",
                #"ffmpeg_location": r'C:\Users\REMOVED_USERNAME\Appbuffer_dir_contents\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe',
                "outtmpl": str(RAW_TRACK_AUDIO_DIR / folder_end),
                "quiet": True,
                "no_warnings": True, 
                "logger": YTDLPLogger(), 
                "match_filters": "duration<=600", # less than 10 minutes
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                }],
            }
            print(f"[{i+1}/{len(songs_to_download)}] dowloading from query: \"{query}\"")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{query}"])
            folder_end = title+".wav"
            if Path(PROJECT_DIR / "raw_track_audio" /  folder_end).exists():
                SONGS_DIR_contents[title]["status"] = "downloaded"
            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
else:
    print("you have enabled the WEAK INTERNET the config, therefore the program wont download anything more.")

#splitting tracks
if not SKIP_SPLIT:
    class DemucsLogger:
        def warning(self, msg):
            print(f"[WARNING] {msg}")

        def error(self, msg):
            print(f"[ERROR] {msg}")

        def progress(self, msg, txt=""):
            if "%" in msg: 
                try:
                    print("\r" + txt + "  [" + str(float(msg.split("|")[2][1:].split(" ")[0].split("/")[0]) / float(msg.split("|")[2][1:].split(" ")[0].split("/")[1]) * 100).split(".")[0] + "%" + "]", end="", flush=True)
                except:
                    print(msg)

    def run_demucs(cmd, logger, txt):
        print(txt, end = "", flush=True)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            line = line.strip()

            # Basic routing logic
            if "error" in line.lower():
                logger.error(line)
            elif "warning" in line.lower():
                logger.warning(line)
            else:
                logger.progress(line, txt)

        process.wait()

        if process.returncode != 0:
            logger.error(f"Demucs exited with code {process.returncode}")
            raise subprocess.CalledProcessError(process.returncode, cmd)

    if CURR_OS == "Windows":
        songs_to_split = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == "downloaded"]
        skip = "no"
        if len(songs_to_split) == 0:
            print("lucky you: there's no audio to split!")
        else:
            print(f"splitting {len(songs_to_split)} tracks, this might take a while...")
        for i in range(len(songs_to_split)):
            title = songs_to_split[i]
            folder_end = title + ".wav"

            if skip in  ["no", "s", "c"]:
                if Path(SEPERATED_DIR / "htdemucs_6s" / title).exists():
                    print("it seems this file already has an output directory, do you still want to process it (if files are overwritten you will be individually warned, dont worry)")
                    while True:
                        skip = input("[s]kip, [c]ontinue anyways, skip [a]ll...")
                        if skip in ["s", "c", "a"]:
                            break
                        else:
                            print("invalid input")
            
            if skip in  ["s", "c"]:
                cmd = [
                    "demucs",
                    RAW_TRACK_AUDIO_DIR / folder_end,
                    "-o",
                    SEPERATED_DIR,
                    "-n",
                    "htdemucs_6s",
                    "--mp3"
                ]

                try:
                    run_demucs(cmd, DemucsLogger(), f"[{i+1}/{len(songs_to_split)}] seperating track: {title}")
                except subprocess.CalledProcessError as e:
                    print("RIP, there was an error")
                    print("Exit code:", e.returncode)
                

            elif skip == "a":
                print("skipping: " + title)
                pass
            
            if Path(SEPERATED_DIR / "htdemucs_6s" / title).exists():
                print()
                print(f"[{i+1}/{len(songs_to_split)}] successfully split the track: {title}")
                SONGS_DIR_contents[title]["status"] = "split"
                print("converting back to wavs for easier processing")

                # converting to wavs
                failure = False
                for mp3_file in Path(SEPERATED_DIR / "htdemucs_6s" / title).rglob("*.mp3"):
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
                    print(f"removing now useless audio: {RAW_TRACK_AUDIO_DIR / folder_end}")
                    Path(RAW_TRACK_AUDIO_DIR / folder_end).unlink()
                    # recording that
                    with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                        json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
                else:
                    print("something went wrong")
            else:
                print("did not split")




    if CURR_OS == "Linux":
        songs_to_split = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == "downloaded"]
        if len(songs_to_split) == 0:
            print("lucky you: there's no audio to split!")
        else:
            print(f"splitting {len(songs_to_split)} tracks, this might take a while...")
            for i in range(len(songs_to_split)):
                title = songs_to_split[i]
                folder_end = title + ".wav"
                cmd = [
                    "demucs",
                    RAW_TRACK_AUDIO_DIR / folder_end,
                    "-o",
                    SEPERATED_DIR,
                    "-n",
                    "htdemucs_6s",
                    "--mp3"
                ]
                try:
                    run_demucs(cmd, DemucsLogger(), f"[{i+1}/{len(songs_to_split)}] seperating track: {title}")
                except subprocess.CalledProcessError as e:
                    print("RIP, there was an error")
                    print("Exit code:", e.returncode)
                if Path(SEPERATED_DIR / "htdemucs_6s" / title).exists():
                    print()
                    print(f"[{i+1}/{len(songs_to_split)}] successfully split the track: {title}")
                    SONGS_DIR_contents[title]["status"] = "split"
                    print("converting back to wavs for easier processing")

                    # converting to wavs
                    failure = False
                    for mp3_file in Path(SEPERATED_DIR / "htdemucs_6s" /  title).rglob("*.mp3"):
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
                        print(f"removing now useless audio: {RAW_TRACK_AUDIO_DIR / folder_end}")
                        Path(RAW_TRACK_AUDIO_DIR / folder_end).unlink()
                        # recording that
                        with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                            json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)
                    else:
                        print("something went wrong")
                else:
                    print("did not split")





# analysing audio to detect stem presence
songs_to_analyse = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] in ["split", "analysed"]]

if len(songs_to_analyse) == 0:
    print("lucky you: there are no songs to analyse!")
else:
    print(f"analysing {len(songs_to_analyse)} songs...")

    analyser = audio_helper.Player_obj(STEMS, SEPERATED_DIR / "htdemucs_6s", volume=70)

    for i in songs_to_analyse:
        analyser.load(i)
        compressed_diag = analyser.analysing_pipeline()
        SONGS_DIR_contents[i]["baked_diagnosis"] = compressed_diag
        SONGS_DIR_contents[i]["status"] = "analysed"
        print(f"[{songs_to_analyse.index(i)}/{len(songs_to_analyse)}] analysed {i}")
        with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
            json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)



print("done with preparations: opening GUI...")
cmd = f"\"{INTERPRETER_PATH}\" \"{SCRIPT_DIR / 'mixer3.1.py'}\" --scale={CF_SCALE}"
subprocess.run(cmd, shell=True)