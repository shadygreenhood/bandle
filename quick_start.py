from constants import WEAK_INTERNET, SKIP_SPLIT, logger, SONGS_JSON_DIR

# cust scripts
import console_backend as scr
from mixer3_1 import main

import json
scr.clear()
logger.pretty_text("╭-------------------------------------------------------------------------------╮\n"\
                   "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       q  u  i  c  k  s  t  a  r  t      |\n"\
                   "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        q  u  i  c  k  s  t  a  r  t      |\n"\
                   "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       q  u  i  c  k  s  t  a  r  t      |\n"\
                   "╰-------------------------------------------------------------------------------╯", "magenta bold")


while True:
    if not scr.add_playlist() == "error":

        with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                SONGS_DIR_contents = json.load(f)
        total = 0
        for i in range(len(SONGS_DIR_contents)):
            if not SONGS_DIR_contents[list(SONGS_DIR_contents.keys())[i]]["status"] == "analysed":
                total += 1
        
        counter = 0
        for i in range(len(SONGS_DIR_contents)):
            
            song = list(SONGS_DIR_contents.keys())[i]
            with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                SONGS_DIR_contents = json.load(f)
            song_status = SONGS_DIR_contents[song]["status"]
            if not song_status == "analysed":
                counter += 1
                logger.pretty_text(f"\[{counter}/{total}]dealing with [bold]{song[:-9]}[/bold]", "magenta")
                logger.debug(f"song_status: {song_status}")
                if song_status == "new" and not WEAK_INTERNET:
                    logger.pretty_text(f"downloading {song[:-9]}", "green italic")
                    song_status = scr.download_songs([song], True, True)
                logger.debug(f"song_status: {song_status}")
                if song_status == "downloaded" and not SKIP_SPLIT:
                    logger.pretty_text(f"splitting {song[:-9]}", "green italic")
                    song_status = scr.split_tracks([song], True, True)
                logger.debug(f"song_status: {song_status}")
                if song_status == "split":
                    logger.pretty_text(f"analysing {song[:-9]}", "green italic")
                    song_status = scr.analyse_tracks([song], True, True)
                


        logger.debug("launching GUI script")
        main()
    else:
        pass