this repository only includes scripts and assets.
this has to be nested in a PROJECT_DIRECTORY, where the program will write output files, you can add fonts, setup you venv, etc...


CONFIG

format: [OPTION]=[VALUE]
there has to be no spaces

Options: 
    SCALE                   (float) factor by which the 950 by 500 screen is getting scaled before printed to the screen
    DEBUG_VLC               (bool) weather to print vlc debug info or not (takes up entire terminal)
    DEFAULT_BLACKLIST       (string) EXACT NAME of the default blacklist you want to set (has to appear in Blacklists.txt)
    CURR_OS                 (Windows / Linux) used to specify which version of the backend script to use (default uses platform.system())


BLACKLSITS

