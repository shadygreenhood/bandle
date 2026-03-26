
from constants import *
from console_backend import *

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
            with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                SONGS_DIR_contents = json.load(f)
            all_song_sorted = list(SONGS_DIR_contents.keys()).sort()

            if all_song_sorted != None and all_song_sorted != []:
                    

                opt1_input = input("1: download all songs\n2: download specific song\n>")
                if opt1_input in ["1", "2"]:
                    if opt1_input == "1":
                        # ALL
                        songs_to_download = [i for i in SONGS_DIR_contents.keys() if SONGS_DIR_contents[i]["status"] == "new"]
                        
                    if opt1_input == "2":
                        with open(SONGS_JSON_DIR, "r", encoding="utf-8") as f:
                            SONGS_DIR_contents = json.load(f)
                        all_song_sorted = list(SONGS_DIR_contents.keys()).sort()
                        
                        while True:
                            selected_song = input("input song name\n>")
                            options = []
                            for i in all_song_sorted:
                                if selected_song in i:
                                    options.append(i)
                            if options != []:
                                if len(options) > 1:
                                    print("muliple options")
                                    for x in options:
                                        print(x[:-9])
                                        print("from ",  SONGS_DIR_contents[x]["artists"])
                                else:
                                    print("selected song is", options[0])
                                    songs_to_download = options[:]
                                    break
                            else:
                                print("no matching songs")
                        
                download_songs(songs_to_download)

            else:
                logger.pretty_text("nothing to download!", "magenta")

        if command == "split_songs":
            split_tracks()
        if command == "analyse_songs":
            analyse_tracks()
    else:
        print(f"command not found: {command}")