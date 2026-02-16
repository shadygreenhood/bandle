from pathlib import Path
import sys
import json


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





buffer_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1playlist_info_buffer.json"
playlists_json_dir = f"{PROJECT_DIR}/{SCRIPT_DIR}/1playlists.json"

with open(buffer_dir, "r", encoding="utf-8") as f:
    data = json.load(f)

tracks = data["tracks"]

cleaned_data = []
for track in tracks:

    artists = track["artists"]
    split = [artists[0]["name"]]
    if len(artists) == 1:
        if "," in artists[0]["name"]:
            split = artists[0]["name"].split(",")
    artists = [{"name": i} for i in split]
    
    cleaned_data.append({
        "name": track["name"],
        "artists": artists
    })

try:
    with open(playlists_json_dir, "r", encoding="utf-8") as f:
        playlists_info = json.load(f)
except:
    playlists_info = {}

playlists_info[data["id"]] = cleaned_data

with open(playlists_json_dir, "w", encoding="utf-8") as f:
    json.dump(playlists_info, f, indent=4, ensure_ascii=False)