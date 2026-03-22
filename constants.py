import sys
from pathlib import Path
# ╭----------------------------------------╮
# |      ╭==╮  ╭==╮  ╭==╮  ╭  ╮  ╭==╮      |
# |      ╞==╯  ╞--╡   ||   ╞--╡  ╰--╮      |
# |      ╰     ╰  ╯   ╰╯   ╰  ╯  ╰==╯      |
# ╰----------------------------------------╯
if getattr(sys, 'frozen', False):
    # Running as EXE
    print("running exe")
    PROJECT_DIR = Path(sys.executable).resolve().parent
    SCRIPT_DIR =            Path(sys._MEIPASS)
else:
    # Running as script
    print("running as script")
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    SCRIPT_DIR =            PROJECT_DIR / "bandle"
    
print(f"porject_dir: {PROJECT_DIR} script_dir: {SCRIPT_DIR}")

INTERPRETER_PATH =      sys.executable

ASSETS_DIR =            SCRIPT_DIR  / "assets"
FFMPEG_DIR =            SCRIPT_DIR  / "ffmpeg"
STEMS_FOLDER =          PROJECT_DIR / "split"
RAW_TRACK_AUDIO_DIR =   PROJECT_DIR / "raw_track_audio"
PLAYLIST_JSON_DIR =     PROJECT_DIR / "playlists.json"
SONGS_JSON_DIR =        PROJECT_DIR / "songs.json"
BLACKLISTS_DIR =        PROJECT_DIR / "Blacklists.txt"
CONFIG_DIR =            PROJECT_DIR / "config.txt"

# adding ffmpeg to path for later
import os
os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ["PATH"]



import pygame   # type:ignore
import platform



DEFAULT_CONFIG =        "SCALE=0.5\n"\
                        "WEAK_INTERNET=False\n"\
                        "SKIP_SPLIT=False\n"\
                        "FONT_DIR=\"font/NotoSansJP-Medium.ttf\""
# creating potentially missing files
if not Path(SONGS_JSON_DIR).exists():
    Path(SONGS_JSON_DIR).write_text("{}")
if not Path(PLAYLIST_JSON_DIR).exists():
    Path(PLAYLIST_JSON_DIR).write_text("{}")
if not Path(CONFIG_DIR).exists():
    Path(CONFIG_DIR).write_text(DEFAULT_CONFIG)

if not Path(STEMS_FOLDER).exists():
    Path(STEMS_FOLDER).mkdir(exist_ok=True)
if not Path(STEMS_FOLDER).exists():
    Path(STEMS_FOLDER).mkdir(exist_ok=True)
if not Path(RAW_TRACK_AUDIO_DIR).exists():
    Path(RAW_TRACK_AUDIO_DIR).mkdir(exist_ok=True)


# ╭------------------------------------------------------------------------------------╮
# |      ╭==╮  ╭  ╮  .       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      |  ╮  |  |  |       |     |  |  |╰╮|  ╰--╮   ||   ╞--╡  |╰╮|   ||   ╰--╮      |
# |      ╰==╯  ╰==╯  ╯       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯   ╰╯   ╰  ╯  ╰ ╰╯   ╰╯   ╰==╯      |
# ╰------------------------------------------------------------------------------------╯
WIDTH = 500
HEIGHT = 950
CATEGORIES =    ["japanese", "pop", "rock", "instrumental"]
STEMS =         ["drums", "bass", "guitar", "piano","other", "vocals"]
SANITIZED_EXEPTIONS = {
    "Undertale_-_Spider_Dance_-_Shirobon_Remix": "Spider Dance",
}
COLOR_PALETTE = {
    "background"            : (255, 255, 255),
    "face"                  : (217, 217, 217),
    "shadow"                : (127, 127, 127),
    "textinput unselected"  : (244, 244, 244),
    "textinput selected"    : (200, 200, 200),
    "list item unselected"  : (183, 183, 183),
    "list item selected"    : (145, 145, 145),
    "black"                 : (0  , 0,   0  ),
    "red accent"            : (195, 63 , 63 ),
    "guessing background"   : (242, 242, 242),
    "stems selected"        : (80 , 80 , 80 )
}



# ╭-------------------------------------------------------------------------------------------------------------╮
# |      ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭    ╭=-       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      |     |  |  |╰╮|  ╰--╮  |  |  |    ╞-        |     |  |  |╰╮|  ╰--╮   ||   ╞--╡  |╰╮|   ||   ╰--╮      |
# |      ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯  ╰==╯  ╰-╯  ╰=-       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯   ╰╯   ╰  ╯  ╰ ╰╯   ╰╯   ╰==╯      |
# ╰-------------------------------------------------------------------------------------------------------------╯
DISALLOWED_CHARS_IN_SANITIZED_TEXT = "<>:\"/\\|?*\x00-\x1F;" # important that no ";" are allowed
CURR_OS = platform.system()





# ╭---------------------------------------╮
# |      ╭=-  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      ╞-   |  |  |╰╮|   ||   ╰--╮      |
# |      ╰    ╰==╯  ╰ ╰╯   ╰╯   ╰==╯      |
# ╰---------------------------------------╯
FONT_DIR = SCRIPT_DIR / "font" / "NotoSansJP-Medium.ttf"
with open(CONFIG_DIR, "r", encoding="utf-8") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "FONT_DIR" in i:
            if len(i.split("=")) > 0:
                try:
                    FONT_DIR = Path(str(i.split('=')[1][1:-1]))
                    if not FONT_DIR.is_absolute():
                        FONT_DIR = SCRIPT_DIR / FONT_DIR
                except:
                    print(f"failed to extract font path in {CONFIG_DIR}")
            else:
                print(f"no path provided after FONT_DIR= in {CONFIG_DIR}")

if not FONT_DIR.exists():
    print(f"Warning: user-specified font not found at {FONT_DIR}, using internal font")
    FONT_DIR = SCRIPT_DIR / "font" / "NotoSansJP-Medium.ttf"

print("font dir: ", FONT_DIR)
print("font dir exists?: ", FONT_DIR.exists())
pygame.font.init()


try:
    small_font = pygame.font.Font(FONT_DIR, 25)
    basic_font = pygame.font.Font(FONT_DIR, 30)
    title_font = pygame.font.Font(FONT_DIR, 60)
except Exception as e:
    print(f"did not load custom font :(\n{e}")
    small_font = pygame.font.SysFont('Comic Sans MS', 25)
    basic_font = pygame.font.SysFont('Comic Sans MS', 30)
    title_font = pygame.font.SysFont('Comic Sans MS', 80)


# ╭----------------------------------------------------------------------------------------------------------------------------------------╮
# |      ╭==╮  ╭   ╮  ╭=-  ╭==╮  ╭  ╮  ╭==╮  .  ╭==╮  ╭==╮  ╭=-.  ╭    ╭=-       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      |  |  '   '  ╞-   ╞=:╯  |╭╮|  ╞=:╯  |   ||   ╞--╡  ╞-:╯  |    ╞-        |     |  |  |╰╮|  ╰--╮   ||   ╞--╡  |╰╮|   ||   ╰--╮      |
# |      ╰==╯   ╰=╯   ╰=-  ╰  ╰  ╰╯╰╯  ╰  ╰  ╯   ╰╯   ╰  ╯  ╰=-╯  ╰-╯  ╰=-       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯   ╰╯   ╰  ╯  ╰ ╰╯   ╰╯   ╰==╯      |
# ╰----------------------------------------------------------------------------------------------------------------------------------------╯
CF_SCALE = 1
CHEAT_MODE = False
GLOBAL_SUGGESTIONS = True
TARGET_FPS = 60
WEAK_INTERNET = False
SKIP_SPLIT = False


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


# ╭---------------------------------------------------------------------------------╮
# |      ╭╮╭╮  .  ╭==╮  ╭=-╮  ╭=-  ╭    ╭    ╭==╮  ╭╮ ╮  ╭=-  ╭==╮  ╭  ╮  ╭==╮      |
# |      |╰╯|  |  ╰--╮  |     ╞-   |    |    ╞--╡  |╰╮|  ╞-   |  |  |  |  ╰--╮      |
# |      ╰  ╯  ╯  ╰==╯  ╰=-╯  ╰=-  ╰-╯  ╰-╯  ╰  ╯  ╰ ╰╯  ╰=-  ╰==╯  ╰==╯  ╰==╯      |
# ╰---------------------------------------------------------------------------------╯

# for downloading songs
class YTDLPLogger:
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(f"[ERROR] {msg}")

def duration_filter(info, *, incomplete):
    duration = info.get("duration")
    
    if duration is None:
        return None  # allow if unknown
    
    if duration > 600:
        return "Video longer than 10 minutes"
    
    return None

# for splitting audio
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

import subprocess
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