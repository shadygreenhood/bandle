
def main_console(q_out=None, q_in=None):
    from constants import clear, SONGS_JSON_DIR, RAW_TRACK_AUDIO_DIR, STEMS_FOLDER, DISALLOWED_CHARS_IN_SANITIZED_TEXT, PLAYLIST_JSON_DIR
    from console_backend import add_playlist, download_songs, split_tracks, analyse_tracks, reset_tracks
    from loggers_init import logger
    import json
    from pathlib import Path
    from time import sleep

    if __name__ == "__main__":
        terminal_logger = logger
        def get_input(str):
            return input(str)
        clear()
    else:
        class terminal_logger():
            def debug(msg):
                q_out.put([["debug", msg]])
            def pretty_text(msg, style):
                q_out.put([["pretty", msg, style]])
            def warning(msg):
                q_out.put([["warning", msg]])
            def error(msg):
                q_out.put([["error", msg]])
        def get_input(str):
            q_out.put([["input", str]])
            while True:
                if not q_in.empty():
                    return q_in.get()


  
    COMMANDS = [
        "help",
        "add_playlist",
        "download_songs",
        "split_songs",
        "analyse_songs",
        "reset_songs",
        "prepare_songs",
        "edit_songs"
    ]


    def choose_songs(target_status, action, only_one=False):

        with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
            SONGS_DIR_contents = json.load(f)


        available_songs = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] in target_status]

        available_songs.sort()

        if available_songs == []:
            return "none"
        else:
            if not only_one:
                terminal_logger.pretty_text("whatcha wanna do?", "magenta")
                terminal_logger.pretty_text(f"1: {action} all songs\n2: {action} specific song", "blue")
                opt1_input = get_input(">")
            else:
                opt1_input = "2"
            if opt1_input in ["1", "2"]:
                output_selection = []
                if opt1_input == "1":
                    if not action == "reset":
                        return available_songs
                    else:
                        terminal_logger.warning("are you SURE?, there is no coming back \[y/n]")
                        opt1_input = get_input(">")
                        if opt1_input == "y":
                            return available_songs
                        else:
                            return []
                if opt1_input == "2":  
                    while True:
                        terminal_logger.pretty_text("here are your options:", "magenta")
                        for x in range(len(available_songs)):
                            terminal_logger.pretty_text(f"{x}: [blue]{available_songs[x][:-9]}[/blue]", "magenta")
                        terminal_logger.pretty_text("get_input song name or number", "magenta")
                        selected_song = get_input(">")
                        if selected_song == "q":
                            return "error"
                        try:
                            options = [(available_songs[int(selected_song)])]
                        except:
                            options = []
                            for i in available_songs:
                                if selected_song.lower() in i[:-9].lower():
                                    options.append(i)
                        if options != []:
                            if len(options) > 1:
                                terminal_logger.pretty_text("your text matched multiple options, \nplease enter the correct one's number\n", "magenta")
                                for x in range(len(options)):
                                    option_text = f"{x}: [blue]{options[x][:-9]}[/blue]  from  [green]{', '.join(SONGS_DIR_contents[options[x]]['artists'])}[/green]"
                                    terminal_logger.pretty_text(option_text, "magenta")
                                opt2_input = get_input(">")
                                try:
                                    if not options[int(opt2_input)] in output_selection:
                                        output_selection.append(options[int(opt2_input)])
                                except Exception as e:
                                    terminal_logger.error(f"there was an error interpreting your get_input: \n\n    {e}")
                            else:
                                terminal_logger.pretty_text(f"selected: {options[0][:-9]}", "magenta")
                                if not options[0] in output_selection:
                                    output_selection.append(options[0])
                        else:
                            terminal_logger.warning("no matching songs")
                        if not only_one:
                            terminal_logger.pretty_text("you have selected:\n - " + "\n - ".join([x[:-9] for x in output_selection]), "magenta")
                            terminal_logger.pretty_text(f"continue selecting? \[y/n]", "magenta")
                            opt3_input = get_input(">")
                            if selected_song == "q":
                                return "error"
                            if not opt3_input.lower() == "y":
                                return output_selection
                        else:
                            return output_selection
            else:
                if opt1_input != "q":
                    terminal_logger.error("unexpected user string: " + opt1_input)
                return "error"

    def console_help():
        terminal_logger.pretty_text("" \
        ".----------------------------------------------------.\n" \
        "this is a simple interface for custom preprocessing   \n "\
        "backend scripts. basically, if you want more control  \n" \
        "over which songs to download, split, analyse, or have \n" \
        "some playlists to add, you've come to the right place!\n" \
        "                                                      \n" \
        "this console gives you access to a bunch of functions:\n" \
        " - add_playlist   : allows you to enter a url, to add \n" \
        "                    its songs to bandle as a new      \n" \
        "                    playlist                          \n" \
        " - download_songs : (first preprocessing step) allows \n" \
        "                    you to download a selection of    \n" \
        "                    songs from your playlists         \n" \
        " - split_songs    : (second preprocessing step) allows\n" \
        "                    you to split desired songs using  \n" \
        "                    demucs                            \n" \
        " - anaylse_songs  : (last processing step) allows you \n" \
        "                    to analyse songs (used for the    \n" \
        "                    waveform visualizer)              \n" \
        " - prepare_songs  : fully processes selected tracks   \n" \
        " - reset_songs    : IRREVERSIBLE: deletes all         \n" \
        "                    processed info on a track         \n" \
        " - edit_songs     : allows you to rename, or change   \n" \
        "                    the audio for a song if the       \n" \
        "                    generated ones arent good         \n" \
        " - help           : displays this message.            \n" \
        "                                                      \n" \
        "                                                      \n" \
        "since this cannot capture keyboardinterrupts, you can \n" \
        "cancel a prompt by typing q in the terminal.          \n" \
        "this unfortunately doesnt allow you to stop in the    \n" \
        "middle of an action (like splitting or downloading),  \n" \
        "so be careful not to launch too many actions at once. \n" \
        "'----------------------------------------------------'\n", "magenta")


    # WELCOME                
    terminal_logger.pretty_text("   ╭---------------------------------------------╮    \n" \
                                "   |      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       |    \n" \
                                "   |      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        |    \n" \
                                "   |      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       |    \n" \
                                "   ╰----╮----------------------------------╭-----╯    \n" \
                                "        |                                  |          \n" \
                                "        |        c  o  n  s  o  l  e       |          \n" \
                                "        |                                  |          \n" \
                                "        ╰----------------------------------╯          \n", "magenta bold")
    
    
    console_help()




    while True:

        user_input = get_input(">")
        command = user_input.split(" ")[0]
        if command in COMMANDS:


            if command == "help":
                console_help()
            if command == "add_playlist":
                add_playlist()
            if command == "download_songs":

                choice = choose_songs(target_status=["new"], action="download")
                if choice == "none":    
                    terminal_logger.pretty_text("nothing to download!", "magenta")
                elif choice != "error":
                    download_songs(choice)

            if command == "split_songs":
                choice = choose_songs(target_status=["downloaded"], action="split")
                if choice == "none":    
                    terminal_logger.pretty_text("nothing to split!", "magenta")
                elif choice != "error":
                    split_tracks(choice, log=terminal_logger, wrapped=False if __name__ == "__main__" else True)

            if command == "analyse_songs":
                choice = choose_songs(target_status=["split"], action="analyse")
                if choice == "none":    
                    terminal_logger.pretty_text("nothing to analyse!", "magenta")
                elif choice != "error":
                    analyse_tracks(choice)
            
            if command == "reset_songs":
                choice = choose_songs(target_status=["split", "downloaded", "new", "analysed"], action="reset")
                if choice == "none":            
                    terminal_logger.pretty_text("nothing to reset! did you import any playlists?", "magenta")
                elif choice != "error":
                    reset_tracks(choice)
            
            if command == "prepare_songs":
                choice = choose_songs(target_status=["split", "downloaded", "new"], action="prepare")
                print(choice)
                if choice == "none":    
                    terminal_logger.pretty_text("nothing to prepare!", "magenta")
                elif choice != "error":
                    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                        SONGS_DIR_contents = json.load(f)
                    relevant_choice = [i for i in choice if SONGS_DIR_contents[i]["status"] == "new"]
                    download_songs(relevant_choice)
                    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                        SONGS_DIR_contents = json.load(f)
                    relevant_choice = [i for i in choice if SONGS_DIR_contents[i]["status"] == "downloaded"]
                    split_tracks(relevant_choice, log=terminal_logger, wrapped=False if __name__ == "__main__" else True)
                    with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                        SONGS_DIR_contents = json.load(f)
                    relevant_choice = [i for i in choice if SONGS_DIR_contents[i]["status"] == "split"]
                    analyse_tracks(relevant_choice)

            if command == "edit_songs":
                choice = choose_songs(target_status=["split", "downloaded", "new", "analysed"], action="edit", only_one=True)
                if choice == "none":    
                    terminal_logger.pretty_text("nothing to edit! did you import any playlists?", "magenta")
                elif choice != "error":
                    terminal_logger.pretty_text("whatcha wanna do?\n" \
                    "1: rename this song\n" \
                    "2: replace audio for this song", "magenta")
                    opt1 = get_input(">")

                    if not opt1 in ["1", "2"]:
                        pass
                    else:
                        if opt1 == "1":
                            terminal_logger.pretty_text(f"enter new name for {choice[0][:-9]}", "magenta")
                            new_name = get_input(">")
                            if new_name == "":
                                terminal_logger.error(f"cannot rename to empty string")
                            for char in new_name:
                                if char in DISALLOWED_CHARS_IN_SANITIZED_TEXT:
                                    terminal_logger.error(f"character {char} is not allowed")
                            

                            # renaming in playlists.json
                            with open(PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
                                PLAYLISTS_DIR_contents = json.load(f)
                            
                            for i in PLAYLISTS_DIR_contents:
                                for j in range(len(PLAYLISTS_DIR_contents[i]["data"])):
                                    if PLAYLISTS_DIR_contents[i]["data"][j]["name"] == choice[0]:
                                        PLAYLISTS_DIR_contents[i]["data"][j]["name"] = new_name+choice[0][-9:]

                            with open(PLAYLIST_JSON_DIR, "w", encoding="utf-8") as f:
                                json.dump(PLAYLISTS_DIR_contents, f, indent=4, ensure_ascii=False)

                            # renaming in songs.json
                            with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                                SONGS_DIR_contents = json.load(f)
                            SONGS_DIR_contents[new_name+choice[0][-9:]] = SONGS_DIR_contents.pop(choice[0])
                            with open(SONGS_JSON_DIR, "w", encoding="utf-8") as f:
                                json.dump(SONGS_DIR_contents, f, indent=4, ensure_ascii=False)

                            # renaming potential raw track audio
                            if Path(RAW_TRACK_AUDIO_DIR / (choice[0] + ".wav")).exists():
                                Path(RAW_TRACK_AUDIO_DIR / (choice[0] + ".wav")).with_stem(new_name)
                            # renaming stems folder
                            if Path(STEMS_FOLDER / choice[0]).exists():
                                Path(STEMS_FOLDER / choice[0]).rename(STEMS_FOLDER / (new_name+choice[0][-9:]))

                            terminal_logger.pretty_text("Done!", "magenta")
                        if opt1 == "2":
                            with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                                SONGS_DIR_contents = json.load(f)
                            terminal_logger.warning(f" RESETTING \"{choice[0][:-9]}\" BY \"{', '.join(SONGS_DIR_contents[choice[0]]['artists'])}\"\n" \
                                        "this is going to remove all current audio from this song, \n" \
                                        "are you sure you want to continue? \[y/n]")
                            opt2 = get_input(">")
                            if opt2 == "y":
                                reset_tracks(choice)
                                terminal_logger.pretty_text("enter a url for the replacement audio. (youtube link)", "magenta")
                                audio_url = get_input(">")
                                if download_songs(choice, url=audio_url) != "error":
                                    terminal_logger.pretty_text("do you want to process that track completely? \[y/n]", "magenta")
                                    opt3 = get_input(">")
                                    if opt3 == "y":
                                        if split_tracks(choice, give_status=True, log=terminal_logger, wrapped=False if __name__ == "__main__" else True) == "split":
                                            analyse_tracks(choice)


        else:
            terminal_logger.error(f"command not found: {command}")



if __name__ == "__main__":
    main_console()