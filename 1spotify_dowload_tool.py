import subprocess
from pathlib import Path
import sys
import json
import yt_dlp
from time import sleep

if "/" in str(Path(__file__)):
    PROJECT_DIR =  "/".join(str(Path(__file__).resolve().parent).split("/")[:-1])
elif "\\" in str(Path(__file__)):
    PROJECT_DIR =  "\\".join(str(Path(__file__).resolve().parent).split("\\")[:-1])
else:
    raise Exception(f"failed to resolve current project directory with cwd={str(Path(__file__))}")
SCRIPT_DIR = "bandle"
CSV_PATH = f"{PROJECT_DIR}/{SCRIPT_DIR}/CSV.txt"
INTERPRETER_PATH = sys.executable
MP3_DATA_DIR = f"{PROJECT_DIR}/mp3s"
ALLOWED_CHARS_IN_SANITIZED_TEXT = "azertyuiopqsdfghjklmwxcvbn1234567890 "

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
class YTDLPLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(f"[ERROR] {msg}")

songs_to_download = [i for i in songs_dir_contents.keys() if songs_dir_contents[i]["status"] != "downloaded"]
for i in range(len(songs_to_download)):
    
    title = songs_to_download[i]
    if songs_dir_contents[title]["status"] == "new":

        artists = songs_dir_contents[songs_to_download[i]]["artists"]
        query = f"{title} {' '.join(artists)} audio"
        ydl_opts = {
        "format": "bestaudio/best",
            #"ffmpeg_location": r'C:\Users\REMOVED_USERNAME\Appbuffer_dir_contents\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe',
            "outtmpl": PROJECT_DIR + "/new_mp3s/"+title+".%(ext)s",
            "quiet": True,           # reduces built-in noise
            "no_warnings": True,     # suppress warnings
            "logger": YTDLPLogger(), # your custom logger
            "match_filters": "duration<=600",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        print(f"[{i+1}/{len(songs_to_download)}] dowloading from query: \"{query}\"")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])
        sleep(3)
        if Path(PROJECT_DIR + "/new_mp3s/"+title+".mp3").exists():
            songs_dir_contents[title]["status"] = "downloaded"
        with open(songs_dir, "w", encoding="utf-8") as f:
            json.dump(songs_dir_contents, f, indent=4, ensure_ascii=False)

#splitting tracks

