import subprocess
from pathlib import Path
import sys
import json
import yt_dlp
from time import sleep
import platform

# constants
if "/" in str(Path(__file__)):
    PROJECT_DIR =  "/".join(str(Path(__file__).resolve().parent).split("/")[:-1])
elif "\\" in str(Path(__file__)):
    PROJECT_DIR =  "\\".join(str(Path(__file__).resolve().parent).split("\\")[:-1])
else:
    raise Exception(f"failed to resolve current project directory with cwd={str(Path(__file__))}")
CURR_OS = platform.system()
SCALE = 0.5
SCRIPT_DIR = "bandle"
CSV_PATH = f"{PROJECT_DIR}/{SCRIPT_DIR}/CSV.txt"
INTERPRETER_PATH = sys.executable
RAW_TRACK_AUDIO_DIR = f"{PROJECT_DIR}/raw_track_audio"
SEPERATED_DIR = f"{PROJECT_DIR}/split"
ALLOWED_CHARS_IN_SANITIZED_TEXT = "azertyuiopqsdfghjklmwxcvbn1234567890 "
WEAK_INTERNET = True

#overriding constants with config
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
out_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1playlist_info_buffer.json"
playlist = input("paste the spotify url you want to add (s for skip):  ")
buffer_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1playlist_info_buffer.json"
playlists_json_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1playlists.json"
songs_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1songs.json"

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
if playlist != "s" and playlist != "":
    cmd = [
        INTERPRETER_PATH,
        "-m",
        "spotify_scraper",
        "playlist",
        playlist,
        "--output",
        out_dir
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Spotify scraper failed, likely non fatal though, continuing...")
        print("Exit code:", e.returncode)

    with open(buffer_dir, "r", encoding="utf-8") as f:
        buffer_dir_contents = json.load(f)

    print("adding playlist: id: " + buffer_dir_contents["id"] + " name: " + santize_string(buffer_dir_contents["name"]))

    tracks = buffer_dir_contents["tracks"]

    data = []
    for track in tracks:

        artists = track["artists"]
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
        with open(playlists_json_dir, "r", encoding="utf-8") as f:
            playlists_json_dir_contents = json.load(f)
    except:
        playlists_json_dir_contents = {}


    playlists_json_dir_contents[buffer_dir_contents["id"]] = {
        "name": buffer_dir_contents["name"], 
        "data": data
        }

    with open(playlists_json_dir, "w", encoding="utf-8") as f:
        json.dump(playlists_json_dir_contents, f, indent=4, ensure_ascii=False)


# ensuring all songs are in songs.json
with open(playlists_json_dir, "r", encoding="utf-8") as f:
    playlists_json_dir_contents = json.load(f)

try:
    with open(songs_dir, "r", encoding="utf-8") as f:
        songs_dir_contents = json.load(f)
except:
    songs_dir_contents = {}

for i in playlists_json_dir_contents:
    for j in playlists_json_dir_contents[i]:
        if j == "data":
            for k in playlists_json_dir_contents[i][j]:
                if not k["name"] in songs_dir_contents:
                    songs_dir_contents[k["name"]] = {"status": "new", "artists": k["artists"]}

with open(songs_dir, 'w', encoding="utf-8") as f:
    json.dump(songs_dir_contents, f, indent=4, ensure_ascii=False)


#dowloading missing songs
if not WEAK_INTERNET:
    class YTDLPLogger:
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(f"[ERROR] {msg}")

    songs_to_download = [i for i in songs_dir_contents.keys() if songs_dir_contents[i]["status"] == "new"]
    for i in range(len(songs_to_download)):
        
        title = songs_to_download[i]
        if songs_dir_contents[title]["status"] == "new":

            artists = songs_dir_contents[songs_to_download[i]]["artists"]
            query = f"{title} {' '.join(artists)} audio"
            ydl_opts = {
            "format": "bestaudio/best",
                #"ffmpeg_location": r'C:\Users\REMOVED_USERNAME\Appbuffer_dir_contents\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe',
                "outtmpl": RAW_TRACK_AUDIO_DIR+"\\"+title+".%(ext)s",
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
            sleep(3)
            if Path(PROJECT_DIR + "/raw_tracks/"+title+".wav").exists():
                songs_dir_contents[title]["status"] = "downloaded"
            with open(songs_dir, "w", encoding="utf-8") as f:
                json.dump(songs_dir_contents, f, indent=4, ensure_ascii=False)

#splitting tracks
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
    songs_to_split = [i for i in songs_dir_contents.keys() if songs_dir_contents[i]["status"] == "downloaded"]
    for i in range(len(songs_to_split)):
        title = songs_to_split[i]

        cmd = [
            "demucs",
            RAW_TRACK_AUDIO_DIR + "\\" + title + ".wav",
            "-o",
            SEPERATED_DIR + "\\",
            "-n",
            "htdemucs_6s",
            "--mp3"
        ]
        try:
            run_demucs(cmd, DemucsLogger(), "seperating track: " + title + f"  [{i+1}/{len(songs_to_split)}]")
        except subprocess.CalledProcessError as e:
            print("RIP, there was an error")
            print("Exit code:", e.returncode)
        if Path(SEPERATED_DIR + "\\" + "htdemucs_6s" + "\\" +  title).exists():
            print()
            print(f"successfully split the track: {title}, [{i+1}/{len(songs_to_split)}]")
            songs_dir_contents[title]["status"] = "split"
            print("converting back to wavs for easier processing")

            # converting to wavs
            failure = False
            for mp3_file in Path(SEPERATED_DIR + "\\" + "htdemucs_6s" + "\\" +  title).rglob("*.mp3"):
                wav_file = mp3_file.with_suffix(".wav")
                result = subprocess.run(
                    ["ffmpeg", "-loglevel", "error", "-i", str(mp3_file), str(wav_file)]
                )
                if result.returncode == 0:
                    mp3_file.unlink()  # delete original
                else:
                    failure = True
            
            if not failure: # check for faliure converting to wavs very unlikely
                print("removing now useless audio: " + RAW_TRACK_AUDIO_DIR + "\\" + title + ".wav")
                Path(RAW_TRACK_AUDIO_DIR + "\\" + title + ".wav").unlink()
                # recording that
                with open(songs_dir, "w", encoding="utf-8") as f:
                    json.dump(songs_dir_contents, f, indent=4, ensure_ascii=False)
            else:
                print("something went wrong")
        else:
            print("did not split")


if CURR_OS == "Linux":
    print("need to write a linux splitter sry")

cmd = f"\"{INTERPRETER_PATH}\" \"{PROJECT_DIR}/{SCRIPT_DIR}/1mixer3.py\" --scale={SCALE}"
subprocess.run(cmd, shell=True)