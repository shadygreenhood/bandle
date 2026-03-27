
def main():
    from constants import clear, logger, SONGS_JSON_DIR
    from console_backend import add_playlist, download_songs, split_tracks, analyse_tracks
    import json

    clear()

    COMMANDS = [
        "help",
        "add_playlist",
        "download_songs",
        "split_songs",
        "analyse_songs"
    ]


    def choose_songs(target_status, action):

        with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
            SONGS_DIR_contents = json.load(f)

        available_songs = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == target_status]
        available_songs.sort()

        if available_songs == []:
            return "none"
        else:
            logger.pretty_text("whatcha wanna do?", "magenta")
            logger.pretty_text(f"1: {action} all songs\n2: {action} specific song", "blue")
            opt1_input = input(">")
            if opt1_input in ["1", "2"]:
                output_selection = []
                if opt1_input == "1":
                    pass
                if opt1_input == "2":  
                    while True:
                        logger.pretty_text("here are your options:", "magenta")
                        for x in range(len(available_songs)):
                            logger.pretty_text(f"{x}: [blue]{available_songs[x][:-9]}[/blue]", "magenta")
                        logger.pretty_text("input song name or number", "magenta")
                        selected_song = input(">")
                        if selected_song == "q":
                            return "error"
                        try:
                            options = [available_songs[int(selected_song)]]
                        except:
                            options = []
                            for i in available_songs:
                                if selected_song.lower() in i.lower():
                                    options.append(i)
                        if options != []:
                            if len(options) > 1:
                                logger.pretty_text("    your text matched multiple options, please enter the correct one's number\n", "magenta")
                                for x in range(len(options)):
                                    option_text = f"{x}: [blue]{options[x][:-9]}[/blue]  from  [green]{', '.join(SONGS_DIR_contents[options[x]]['artists'])}[/green]"
                                    logger.pretty_text(option_text, "magenta")
                                opt2_input = input(">")
                                try:
                                    if not options[int(opt2_input)] in output_selection:
                                        output_selection.append(options[int(opt2_input)])
                                except Exception as e:
                                    logger.error(f"there was an error interpreting your input: \n\n    {e}")
                            else:
                                logger.pretty_text(f"selected: {options[0][:-9]}", "magenta")
                                output_selection = options[:]
                        else:
                            logger.warning("no matching songs")
                        logger.pretty_text(f"continue selecting? \[y/n]    (selected: {', '.join([x[:-9] for x in output_selection])})", "magenta")
                        opt3_input = input(">")
                        if selected_song == "q":
                            return "error"
                        if not opt3_input.lower() == "y":
                            return output_selection
            else:
                if opt1_input != "q":
                    logger.error("unexpected user string: " + opt1_input)
                return "error"

    def console_help():
        logger.pretty_text("" \
        "this is a simple interface for custom preprocessing backend scripts.\n" \
        "basically, if you want more control over which songs to download, \n" \
        "split, analyse, or have some playlists to add, you've come to the right place!\n" \
        "\n" \
        "this console gives you access to a bunch of functions:\n" \
        "   - add_playlist   : allows you to enter a url, to add its songs to bandle as a new playlist\n" \
        "   - download_songs : (first preprocessing step) allows you to download a selection of songs from your playlists\n" \
        "   - split_songs    : (second preprocessing step) allows you to split desired songs using demucs\n" \
        "   - anaylse_songs  : (last processing step) allows you to analyse songs (used for the waveform visualizer)\n" \
        "   - help           : displays this message.\n" \
        "\n" \
        "\n" \
        "since this cannot capture keyboardinterrupts, you can cancel a prompt by typing q in the terminal.\n" \
        "this unfortunately doesnt allow you to stop in the middle of an action (like splitting or downloading),\n" \
        "so be careful not to launch too many actions at once."
        "\n", "magenta")


    # WELCOME
    logger.pretty_text("╭----------------------------------------------------------------------╮\n" \
                    "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       c  o  n  s  o  l  e      |\n" \
                    "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        c  o  n  s  o  l  e      |\n" \
                    "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       c  o  n  s  o  l  e      |\n" \
                    "╰----------------------------------------------------------------------╯\n", "magenta bold")
    console_help()




    while True:

        user_input = input(">")
        command = user_input.split(" ")[0]
        if command in COMMANDS:


            if command == "help":
                console_help()
            if command == "add_playlist":
                add_playlist()
            if command == "download_songs":

                choice = choose_songs(target_status="new", action="download")
                if choice == "none":    
                    logger.pretty_text("nothing to download!", "magenta")
                elif choice != "error":
                    download_songs(choice)

            if command == "split_songs":
                choice = choose_songs(target_status="downloaded", action="split")
                if choice == "none":    
                    logger.pretty_text("nothing to split!", "magenta")
                elif choice != "error":
                    split_tracks(choice)

            if command == "analyse_songs":
                choice = choose_songs(target_status="split", action="analyse")
                if choice == "none":    
                    logger.pretty_text("nothing to analyse!", "magenta")
                elif choice != "error":
                    analyse_tracks(choice)
        else:
            logger.error(f"command not found: {command}")



if __name__ == "__main__":
    main()