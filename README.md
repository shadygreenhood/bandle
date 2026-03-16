# A Cool Bandle Clone

This repository contains the scripts and assets for the Bandle clone i made.

**notice** This is NOT an original idea, and was *borrowed* from the Bandle app (here is their website: https://bandle.app/menu)
I do not intend to make any money from this, nor do i intend to compete with the original project: this was simply a fun project of mine, that i only made public for the sake of it.

**Important:** This repository must be nested inside a PROJECT_DIRECTORY. The program will write output files here. You can also add fonts, set up a virtual environment, and manage other project-specific files in this directory.

## Configuration

Configurations are set in the format:

OPTION=VALUE

No spaces are allowed around =.


| Option | Type | Description |
|--------|------|-------------|
| SCALE | float | Factor by which the 950×500 screen is scaled before being printed to screen |
| DEBUG_VLC | bool | Whether to print VLC debug info (can fill the entire terminal) |
| DEFAULT_BLACKLIST | string | Exact name of the default blacklist (must exist in Blacklists.txt) |
| CURR_OS | Windows / Linux | Specifies which version of the backend script to use (default: platform.system()) |
| TARGET_FPS | float | Defaults to 60; FPS that the program tries to run at |


## Blacklists
Blacklists are used to track songs you've played so that they are not repeated.
Blacklist details are stored in Blacklists.txt with the format:

BLACKLIST_NAME=song1;song2;...

SECOND_BLACKLIST_NAME=song1;song2;...

...

## Installation Details

The script expects the following folder structure:
```
PROJECT_DIRECTORY/
│
├─ bandle/              # This repository
│   ├─ assets/
│   ├─ [other scripts]
│   └─ ...
│
├─ raw_track_audio/     # Generated folder
└─ split/               # Generated folder
```
The script writes files to the parent directory of this repository.

## Installation

Clone the repository:
```
git clone https://github.com/shadygreenhood/bandle
cd bandle
```
(Recommended) Create a separate virtual environment:
```
python3.10 -m venv .venv3.10
```
Activate the virtual environment:

Windows:
```
.venv3.10\Scripts\activate
```
Linux:
```
source .venv3.10/bin/activate.sh
```
Install the required Python libraries:
```
pip install -r requirements.txt
```

## Running the Game

There are two main scripts:

bandle.py – The main configuration script, meant to be run at initialization.

mixer.py – Only the GUI; does not prepare audio files.

### Recommended:
Activate your virtual environment (if you created one) and run:

```
python bandle.py
```
