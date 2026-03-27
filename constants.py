import sys
from pathlib import Path
import os
import pygame   # type:ignore
import certifi

# Logger
from loggers_init import *

clear()
logger.pretty_text("this should be pretty. . . ", "magenta italic bold")

logger.pretty_text("╭--------------------------------------------------------------------------------╮\n" \
                   "|      ╭    ╭==╮  ╭==╮  ╭-.   .   ╭╮ ╮  ╭=-       c  o  n  s  t  a  n  t  s      |\n" \
                   "|      |    |  |  ╞--╡  |  |  |   |╰╮|  |  ╮      c  o  n  s  t  a  n  t  s      |\n" \
                   "|      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯   ╰ ╰╯  ╰=-╯      c  o  n  s  t  a  n  t  s      |\n" \
                   "╰--------------------------------------------------------------------------------╯", "magenta bold")



# ╭----------------------------------------╮
# |      ╭==╮  ╭==╮  ╭==╮  ╭  ╮  ╭==╮      |
# |      ╞==╯  ╞--╡   ||   ╞--╡  ╰--╮      |
# |      ╰     ╰  ╯   ╰╯   ╰  ╯  ╰==╯      |
# ╰----------------------------------------╯
logger.debug("Defining paths")

if getattr(sys, 'frozen', False):
    # Running as EXE
    PROJECT_DIR = Path(sys.executable).resolve().parent
    SCRIPT_DIR =            Path(sys._MEIPASS)
else:
    # Running as script
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    SCRIPT_DIR =            PROJECT_DIR / "bandle"

INTERPRETER_PATH =      sys.executable

ASSETS_DIR =            SCRIPT_DIR  / "assets"
FFMPEG_DIR =            SCRIPT_DIR  / "ffmpeg"
STEMS_FOLDER =          PROJECT_DIR / "split"
RAW_TRACK_AUDIO_DIR =   PROJECT_DIR / "raw_track_audio"
PLAYLIST_JSON_DIR =     PROJECT_DIR / "playlists.json"
SONGS_JSON_DIR =        PROJECT_DIR / "songs.json"
BLACKLISTS_DIR =        PROJECT_DIR / "Blacklists.txt"
CONFIG_DIR =            PROJECT_DIR / "config.txt"

if getattr(sys, 'frozen', False):
    logger.debug("Adding bundled ffmpeg to PATH")
    os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ["PATH"]

    logger.debug("setting up SSL_CERT_FILE, ")

    os.environ["SSL_CERT_FILE"] = certifi.where()


DEFAULT_CONFIG =        "SCALE=0.5\n"\
                        "WEAK_INTERNET=False\n"\
                        "SKIP_SPLIT=False\n"\
                        "FONT_DIR=\"font/NotoSansJP-Medium.ttf\""

logger.debug("creating potentially missing files")
if not Path(SONGS_JSON_DIR).exists():
    logger.debug(f"creating songs.json: {SONGS_JSON_DIR}")
    Path(SONGS_JSON_DIR).write_text("{}")
if not Path(PLAYLIST_JSON_DIR).exists():
    logger.debug(f"creating playlists.json: {PLAYLIST_JSON_DIR}")
    Path(PLAYLIST_JSON_DIR).write_text("{}")
if not Path(CONFIG_DIR).exists():
    logger.debug(f"creating config.txt: {CONFIG_DIR}")
    Path(CONFIG_DIR).write_text(DEFAULT_CONFIG)


if not Path(STEMS_FOLDER).exists():
    logger.debug(f"creating STEMS_FOLDER: {STEMS_FOLDER}")
    Path(STEMS_FOLDER).mkdir(exist_ok=True)
if not Path(RAW_TRACK_AUDIO_DIR).exists():
    logger.debug(f"creating RAW_TRACK_AUDIO_DIR: {RAW_TRACK_AUDIO_DIR}")
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
logger.debug("identifying current OS")
import platform
CURR_OS = platform.system()
logger.debug(f"current OS seems to  be {CURR_OS}")


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
                    logger.error(f"failed to extract font path in {CONFIG_DIR}")
            else:
                logger.error(f"no path provided after FONT_DIR= in {CONFIG_DIR}")

if not FONT_DIR.exists():
    logger.warning(f"Warning: user-specified font not found at {FONT_DIR}, using internal font")
    FONT_DIR = SCRIPT_DIR / "font" / "NotoSansJP-Medium.ttf"

pygame.font.init()

try:
    small_font = pygame.font.Font(FONT_DIR, 25)
    basic_font = pygame.font.Font(FONT_DIR, 30)
    title_font = pygame.font.Font(FONT_DIR, 60)
except Exception as e:
    logger.error(f"did not load custom font :(\n{e}")
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
curr_blacklist = -1

# creating potentially missing files
if not Path(BLACKLISTS_DIR).exists():
    Path(BLACKLISTS_DIR).write_text("")

# read Blacklists.txt
global BLACKLISTS_NAMES
BLACKLISTS_NAMES = []
with open(BLACKLISTS_DIR, "r", encoding="utf-8") as f:
    txt = f.read().splitlines()
    BLACKLISTS = []
    for i in txt:
        try:
            BLACKLISTS.append([j for j in i.split("=")[1].split(";")])
            BLACKLISTS_NAMES.append(i.split("=")[0])
        except:
            help(f"failed to extract contents of {i} in Blacklists.txt")
        if BLACKLISTS[-1][-1] == "":
            BLACKLISTS[-1].pop(-1)
if BLACKLISTS == []:
    print("no blacklists found in Blacklist.txt, creating a new one")
    with open(BLACKLISTS_DIR, "w", encoding="utf-8") as f:
        f.write("DEFAULT=")
    BLACKLISTS = [[""]]
    BLACKLISTS_NAMES = ["DEFAULT"]



#overriding constants with config
with open(PROJECT_DIR / "config.txt", "r") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "SCALE" in i:
            if len(i.split("=")) > 0:
                CF_SCALE = float(i.split("=")[1])
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
        if "TARGET_FPS" in i:
            if len(i.split("=")) > 0:
                try:
                    TARGET_FPS = float(i.split("=")[1]) if float(i.split("=")[1]) > 0 else TARGET_FPS
                except:
                    help(f"failed to convert" + str(i.split("=")[1]) + "to a float")
            else:
                help(f"no target fps provided in {CONFIG_DIR} after con.TARGET_FPS=")
        if "DEFAULT_BLACKLIST" in i:
            if len(i.split("=")) > 0:
                curr_blacklist = str(i.split("=")[1])
                if curr_blacklist in BLACKLISTS_NAMES:
                    curr_blacklist = BLACKLISTS_NAMES.index(curr_blacklist)
                else:
                    help(f"default blacklist is set to an unknown value in {CONFIG_DIR}")
            else:
                help(f"no blacklist provided after DEFAULT_BLACKLIST= in {BLACKLISTS_DIR}")

if curr_blacklist == -1:
    logger.debug("no default blacklist found in config.txt defaulting to the first")
    curr_blacklist = 0

# filtering possible OSes
if CURR_OS == "Windows":
    logger.debug("running windows script")
else:
    if CURR_OS == "Linux":
        logger.debug("running linux script")
    else:
        logger.warning("os not recognised, defaulting to linux script")
        CURR_OS = "Linux"
