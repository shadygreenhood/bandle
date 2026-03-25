
from pathlib import Path


# from constants import *

COMMANDS = [
    "help",
    "add_playlist",
    "download_songs",
    "split_songs",
    "analyse_songs"
]

def help(args):
    print("\n ")
    # check arg validity
    
    if args != []:
        print("no arguments needed")


    print(f"help message\n playlist-cli")

def playlist_cli(args):
    print("playlist_cli script")

    # check arg validity

    if args == []:
        print("playlist_cli help \n\
              options: \n\
              ")

    if "-r" in args:

        if args.index("-r") + 1 < len(args):
            type = args[args.index("-r") + 1]
            args.pop(args.index("-r") + 1)

            if not type in ["song", "playlist"]:
                print("type not recognised")
            else:

                og = args[args.index("-r") + 1]
                args.pop(args.index("-r") + 1)
                new = args[args.index("-r") + 1]
                args.pop(args.index("-r") + 1)

                print(f"renaming {og} to {new}")
        else:
            print("og and new need to b provided")

        args.pop(args.index("-r"))


    if "-a" in args:

        if args.index("-a") + 1 < len(args):
            url = args[args.index("-a") + 1]
            args.pop(args.index("-a") + 1)

            print(f"adding playlist from url: {url}")
        else:
            print("need a playlist url")

        args.pop(args.index("-a"))



    if args != []:
        print(f"args {args} were not dealt with")



print("opening console")
# pretty intro

while True:
    
    command = input("   ->")
    if  command.split(" ")[0] in COMMANDS:
        args = command.split(" ")[1:]
        args = [x for x in args if x]

        if command.split(" ")[0] == "help":
            help(args)
        elif command.split(" ")[0] == "playlist-cli":
            playlist_cli(args)
    else:
        print(f"command {command.split(' ')[0]} not found")

