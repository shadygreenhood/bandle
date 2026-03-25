from constants import WEAK_INTERNET, SKIP_SPLIT, logger

# cust scripts
logger.debug("loading custom scripts")
from mixer3_1 import main
import console_backend as scr


scr.clear()
logger.pretty_text("╭-----------------------------------------------------------------------------------------╮\n"\
                   "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭    ╭=-      |\n"\
                   "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        |     |  |  |╰╮|  ╰--╮  |  |  |    ╞-       |\n"\
                   "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯  ╰==╯  ╰-╯  ╰=-      |\n"\
                   "╰-----------------------------------------------------------------------------------------╯", "magenta bold")

if not scr.add_playlist() == "error":


    #dowloading missing songs
    if not WEAK_INTERNET:
        scr.download_songs()
    else:
        logger.pretty_text("you have enabled WEAK INTERNET in the config, therefore the program won't download anything more.", "magenta")


    if not SKIP_SPLIT:
        scr.split_tracks()
    else:
        logger.pretty_text("you have enabled the SKIP_SPLIT in the config, therefore the program won't split tracks.", "magenta")


    scr.analyse_tracks()


    logger.debug("launching GUI script")
    main()