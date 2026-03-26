from constants import WEAK_INTERNET, SKIP_SPLIT, logger, SONGS_JSON_DIR

# cust scripts
logger.debug("loading custom scripts")
from mixer3_1 import main
import console_backend as scr

import json
scr.clear()
logger.pretty_text("╭-----------------------------------------------------------------------------------------╮\n"\
                   "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭    ╭=-      |\n"\
                   "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        |     |  |  |╰╮|  ╰--╮  |  |  |    ╞-       |\n"\
                   "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯  ╰==╯  ╰-╯  ╰=-      |\n"\
                   "╰-----------------------------------------------------------------------------------------╯", "magenta bold")



if not scr.add_playlist() == "error":

    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
            SONGS_DIR_contents = json.load(f)

    for song in list(SONGS_DIR_contents.keys()):
        logger.pretty_text(f"dealing with [bold]{song[:-9]}[/bold]", "magenta")
        if SONGS_DIR_contents[song]["status"] == "new" and not WEAK_INTERNET:
            logger.pretty_text(f"downloading {song[:-9]}", "green italic")
            scr.download_songs([song], True)
        if SONGS_DIR_contents[song]["status"] == "downloaded" and not SKIP_SPLIT:
            logger.pretty_text(f"splitting {song[:-9]}", "green italic")
            scr.split_tracks([song], True)
        if SONGS_DIR_contents[song]["status"] == "split":
            logger.pretty_text(f"analysing {song[:-9]}", "green italic")
            scr.analyse_tracks([song], True)






    logger.debug("launching GUI script")
    main()