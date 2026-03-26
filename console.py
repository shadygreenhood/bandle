
from constants import *
from console_backend import *

clear()



COMMANDS = [
    "help",
    "add_playlist",
    "download_songs",
    "split_songs",
    "analyse_songs"
]



while True:

    user_input = input(">")
    command = user_input.split(" ")[0]
    if command in COMMANDS:


        if command == "help":
            help()
        if command == "add_playlist":
            add_playlist()
        if command == "download_songs":
# ╭--------------------------------------------------------------------------------------------------------------╮
# |      ╭-.   ╭==╮  ╭  ╮  ╭╮ ╮  ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  .  ╭==╮  ╭==╮      |
# |      |  |  |  |  |╭╮|  |╰╮|  |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  |  ╞==╯   ||       |
# |      ╰='   ╰==╯  ╰╯╰╯  ╰ ╰╯  ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╯  ╰      ╰╯       |
# ╰--------------------------------------------------------------------------------------------------------------╯
            has_he_quit_yet = False



            with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                SONGS_DIR_contents = json.load(f)

            downloadable_songs = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == "new"]


            if downloadable_songs != []:
                logger.pretty_text("whatcha wanna do?", "magenta")
                logger.pretty_text("1: download all songs\n2: download specific song", "blue")
                opt1_input = input(">")


                if opt1_input in ["1", "2"]:
                    songs_to_download = []
                    if opt1_input == "1":
                        pass
                    if opt1_input == "2":  
                        while True:
                            logger.pretty_text("here are your options:", "magenta")
                            for x in range(len(downloadable_songs)):
                                logger.pretty_text(f"{x}: [blue]{downloadable_songs[x][:-9]}[/blue]", "magenta")
                            logger.pretty_text("input song name or number", "magenta")
                            selected_song = input(">")


                            if selected_song == "q":
                                has_he_quit_yet = True
                            try:
                                options = [downloadable_songs[int(selected_song)]]
                            except:
                                options = []
                                for i in downloadable_songs:
                                    if selected_song.lower() in i.lower():
                                        options.append(i)

                            if options != [] and has_he_quit_yet == False:
                                if len(options) > 1:
                                    logger.pretty_text("    your text matched multiple options, please enter the correct one's number\n", "magenta")
                                    for x in range(len(options)):
                                        option_text = f"{x}: [blue]{options[x][:-9]}[/blue]  from  [green]{', '.join(SONGS_DIR_contents[options[x]]['artists'])}[/green]"
                                        logger.pretty_text(option_text, "magenta")
                                    opt2_input = input(">")




                                    try:
                                        if not options[int(opt2_input)] in songs_to_download:
                                            songs_to_download.append(options[int(opt2_input)])
                                    except Exception as e:
                                        logger.error(f"there was an error interpreting your input: \n\n    {e}")
                                else:
                                    logger.pretty_text(f"selected: {options[0][:-9]}", "magenta")
                                    songs_to_download = options[:]
                            else:
                                if not has_he_quit_yet:
                                    logger.warning("no matching songs")


                            if has_he_quit_yet:
                                break
                            else:
                                logger.pretty_text(f"continue selecting? \[y/n]    (selected: {', '.join([x[:-9] for x in songs_to_download])})", "magenta")
                                opt3_input = input(">")

                                if selected_song == "q":
                                    has_he_quit_yet = True
                                if not opt3_input.lower() == "y":
                                    break

                else:
                    if opt1_input != "q":
                        logger.error("unexpected user string: " + opt1_input)
                    has_he_quit_yet = True

                if not has_he_quit_yet:        
                    download_songs(songs_to_download)

            else:
                logger.pretty_text("nothing to download!", "magenta")

        if command == "split_songs":
            split_tracks()
        if command == "analyse_songs":
            analyse_tracks()
    else:
        logger.error(f"command not found: {command}")