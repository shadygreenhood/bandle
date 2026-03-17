import pygame
import platform
import sys

from pathlib import Path


# ╭----------------------------------------╮
# |      ╭==╮  ╭==╮  ╭==╮  ╭  ╮  ╭==╮      |
# |      ╞==╯  ╞--╡   ||   ╞--╡  ╰--╮      |
# |      ╰     ╰  ╯   ╰╯   ╰  ╯  ╰==╯      |
# ╰----------------------------------------╯
INTERPRETER_PATH =      sys.executable
PROJECT_DIR =           Path(__file__).resolve().parent.parent
SCRIPT_DIR =            PROJECT_DIR / "bandle"
ASSETS_DIR =            SCRIPT_DIR  / "assets"
STEMS_FOLDER =          PROJECT_DIR / "split" / "htdemucs_6s"
RAW_TRACK_AUDIO_DIR =   PROJECT_DIR / "raw_track_audio"
SEPERATED_DIR =         PROJECT_DIR / "split"
PLAYLIST_JSON_DIR =     PROJECT_DIR / "playlists.json"
SONGS_JSON_DIR =        PROJECT_DIR / "songs.json"
BUFFER_DIR =            PROJECT_DIR / "playlist_info_buffer.json"
BLACKLISTS_DIR =        PROJECT_DIR / "Blacklists.txt"
CONFIG_DIR =            PROJECT_DIR / "config.txt"
FONT_DIR =              "None"      # extracted from config in GUI

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
DEFAULT_CONFIG =        "SCALE=0.5\nWEAK_INTERNET=False\nSKIP_SPLIT=False\nFONT_DIR=\"bandle/font/NotoSansJP-Medium.ttf\""
ALLOWED_CHARS_IN_SANITIZED_TEXT = "azertyuiopqsdfghjklmwxcvbn1234567890 " # important that no ";" are allowed
CURR_OS = platform.system()





# ╭---------------------------------------╮
# |      ╭=-  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮      |
# |      ╞-   |  |  |╰╮|   ||   ╰--╮      |
# |      ╰    ╰==╯  ╰ ╰╯   ╰╯   ╰==╯      |
# ╰---------------------------------------╯

with open(CONFIG_DIR, "r", encoding="utf-8") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "FONT_DIR" in i:
            if len(i.split("=")) > 0:
                try:
                    FONT_DIR = str(i.split("=")[1][1:-1])
                except:
                    print(f"failed to extract font path in {CONFIG_DIR}")
            else:
                print(f"no path provided after FONT_DIR= in {CONFIG_DIR}")

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
CF_DEBUG_VLC = False
TARGET_FPS = 60
WEAK_INTERNET = False
SKIP_SPLIT = False

