

def main():
    

    import constants as con

    con.logger.pretty_text("╭-------------------------------------------------╮\n"\
                           "|      ╭    ╭==╮  ╭==╮  ╭-.   .   ╭╮ ╮  ╭=-       |\n"\
                           "|      |    |  |  ╞--╡  |  |  |   |╰╮|  |  ╮      |\n"\
                           "|      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯   ╰ ╰╯  ╰=-╯      |\n"\
                           "╰-------------------------------------------------╯", "magenta bold")
    con.logger.debug("loading custom scripts")

    import audio_helper as audio_helper
    from modules import Button, Toggle, Textinput, Warning
    

    con.logger.debug("loading pygame")
    import pygame           # type: ignore
    con.logger.debug("loading math")
    import math
    con.logger.debug("loading json")
    import json

    con.logger.debug("loading shuffle (random)")
    from random import shuffle
    con.logger.debug("loading argv (sys)")
    from sys import argv
    from time import sleep, perf_counter
    con.logger.debug("loading Path (pathlib)")
    from pathlib import Path

    con.clear()
    con.logger.pretty_text("╭-----------------------------------------------------------------------------------------╮\n"\
                           "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       ╭=-╮  ╭==╮  ╭╮ ╮  ╭==╮  ╭==╮  ╭    ╭=-      |\n"\
                           "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        |     |  |  |╰╮|  ╰--╮  |  |  |    ╞-       |\n"\
                           "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       ╰=-╯  ╰==╯  ╰ ╰╯  ╰==╯  ╰==╯  ╰-╯  ╰=-      |\n"\
                           "╰-----------------------------------------------------------------------------------------╯", "magenta bold")



    global curr_blacklist
    curr_blacklist = -1
    global mouse_scroll
    global mouse_x
    global mouse_y
    mouse_scroll, mouse_x, mouse_y = 0, 0, 0
    global k_up
    global k_down
    k_up, k_down = 0, 0




    # creating potentially missing files
    if not Path(con.BLACKLISTS_DIR).exists():
        Path(con.BLACKLISTS_DIR).write_text("")

    # read Blacklists.txt
    global blacklists
    global blacklist_names
    blacklist_names = []
    with open(con.BLACKLISTS_DIR, "r", encoding="utf-8") as f:
        txt = f.read().splitlines()
        blacklists = []
        for i in txt:
            try:
                blacklists.append([j for j in i.split("=")[1].split(";")])
                blacklist_names.append(i.split("=")[0])
            except:
                con.help(f"failed to extract contents of {i} in Blacklists.txt")
            if blacklists[-1][-1] == "":
                blacklists[-1].pop(-1)
    if blacklists == []:
        print("no blacklists found in Blacklist.txt, creating a new one")
        with open(con.BLACKLISTS_DIR, "w", encoding="utf-8") as f:
            f.write("DEFAULT=")
        blacklists = [[""]]
        blacklist_names = ["DEFAULT"]

    # read config
    with open(con.CONFIG_DIR, "r", encoding="utf-8") as f:
        txt = f.read().splitlines()
        for i in txt:
            if "SCALE" in i:
                if len(i.split("=")) > 0:
                    try:
                        con.CF_SCALE = float(i.split("=")[1])
                    except:
                        con.help("failed to convert " + str(i.split("=")[1]) + "to a float" )
                else:
                    con.help(f"no scale provided in {con.CONFIG_DIR} after SCALE=")
            if "TARGET_FPS" in i:
                if len(i.split("=")) > 0:
                    try:
                        con.TARGET_FPS = float(i.split("=")[1]) if float(i.split("=")[1]) > 0 else con.TARGET_FPS
                    except:
                        help(f"failed to convert" + str(i.split("=")[1]) + "to a float")
                else:
                    con.help(f"no target fps provided in {con.CONFIG_DIR} after con.TARGET_FPS=")
            if "DEFAULT_BLACKLIST" in i:
                if len(i.split("=")) > 0:
                    curr_blacklist = str(i.split("=")[1])
                    if curr_blacklist in blacklist_names:
                        curr_blacklist = blacklist_names.index(curr_blacklist)
                    else:
                        con.help(f"default blacklist is set to an unknown value in {con.CONFIG_DIR}")
                else:
                    con.help(f"no blacklist provided after DEFAULT_BLACKLIST= in {con.BLACKLISTS_DIR}")

    if curr_blacklist == -1:
        con.logger.debug("no default blacklist found in config.txt defaulting to the first")
        curr_blacklist = 0

    # deal with flags
    args = argv[1:]
    for i in args:
        if i.startswith('--scale='):
            if len(i.split("=", 1)) > 0:
                con.CF_SCALE = float(i.split("=", 1)[1])
            else:
                con.help("no scale provided")
        else:
            con.help("argument not recognized")
        




    with open(con.PLAYLIST_JSON_DIR, "r", encoding="utf-8") as f:
        global playlists_json_dir_contents
        playlists_json_dir_contents = json.load(f)

    with open(con.SONGS_JSON_DIR, "r", encoding="utf-8") as f:
        con.SONGS_JSON_DIR_contents = json.load(f)

    global all_songs
    all_songs = list(con.SONGS_JSON_DIR_contents.keys())

    def sanitize(text):
        return "".join(text.split("_")[:-1]) if not "".join(text.split("_")[:-1]) == "" else text

    global all_songs_sanitized
    all_songs_sanitized = []

    for i in all_songs:
        sanitized = sanitize(i)
        all_songs_sanitized.append(sanitized)

    # ╭----------------------------------------╮
    # |      ╭----   ╭----╮ ╭-╮╭-╮ ╭----       |
    # |      |       |    | | ╰╯ | |           |
    # |      |    ╮  |----| |    | |--         |
    # |      |    |  |    | |    | |           |
    # |      ╰----╯  ╰    ╯ ╰    ╯ ╰----       |
    # ╰----------------------------------------╯

    # pygame setup
    pygame.init()
    pygame.font.init()
    pygame.key.start_text_input()

    global screen
    global running
    global clock
    global window
    window = pygame.display.set_mode((con.WIDTH*con.CF_SCALE, con.HEIGHT*con.CF_SCALE)) 
    screen = pygame.Surface((con.WIDTH, con.HEIGHT))
    clock = pygame.time.Clock()
    running = True

    # ╭----------------------------------------╮
    # |      ╭----╮  ╭    ╮ ╭--.  ╭---╮ ╭----╮ |
    # |      |    |  |    | |   ¡   |   |    | |
    # |      |----|  |    | |   |   |   |    | |
    # |      |    |  |    | |   !  _|_  |    | |
    # |      ╰    ╯  ╰----╯ ╰--'  ╰---╯ ╰----╯ |
    # ╰----------------------------------------╯

    global player
    player = audio_helper.Player_obj(con.STEMS, con.STEMS_FOLDER, volume=6)

    # ╭--------------------------------------------------------------------╮
    # |      ╭----   ╭----╮ ╭-╮╭-╮ ╭----     ╭---╮  ╭╮   ╮ ╭---╮ ╭---╮     |
    # |      |       |    | | ╰╯ | |           |    |╰╮  |   |     |       |
    # |      |    ╮  |----| |    | |--         |    | ╰╮ |   |     |       |
    # |      |    |  |    | |    | |          _|_   |  ╰╮|  _|_    |       |
    # |      ╰----╯  ╰    ╯ ╰    ╯ ╰----     ╰---╯  ╰   ╰╯ ╰---╯   |       |
    # ╰--------------------------------------------------------------------╯

    def scale_mouse_pos(pos):
        return (pos[0]*(1/con.CF_SCALE),pos[1]*(1/con.CF_SCALE))




    # ╭---------------------------------------------------------------------╮
    # |      ╭----   ╭----╮ ╭-╮╭-╮ ╭----     ╭     ╭----╮ ╭----╮ ╭----╮     |
    # |      |       |    | | ╰╯ | |         |     |    | |    | |    |     |
    # |      |    ╮  |----| |    | |--       |     |    | |    | |----╯     |
    # |      |    |  |    | |    | |         |     |    | |    | |          |
    # |      ╰----╯  ╰    ╯ ╰    ╯ ╰----     ╰---╯ ╰----╯ ╰----╯ ╰          |
    # ╰---------------------------------------------------------------------╯

    def skip(silent=False, skip_song=False, simple_update=False):
            global _b_step
            global _b_song_counter
            global _b_queue
            global _b_current_song
            global curr_screen
            global player
            _b_step += 1
            if not _b_step > len(con.STEMS) and not skip_song:
                if simple_update:
                    player.update_to_play(_b_step)
                else:
                    
                    player.play(_b_step)
                    player.seek(player.audio_len/5)
                    player.toggle()
                
            if _b_step > len(con.STEMS) or skip_song:
                player.stop_all()
                _b_step = 1

                # update the correct blacklist
                with open(con.BLACKLISTS_DIR, "r", encoding="utf-8") as f:
                    txt = f.read()
                txts=txt.splitlines()
                buffer = ""
                for i in range(len(txts)):
                    if i == curr_blacklist:
                        buffer += txts[i] + _b_current_song + ";" + "\n"
                    else:
                        buffer += txts[i] + "\n"
                with open(con.BLACKLISTS_DIR, "w", encoding="utf-8") as f:
                    f.write(buffer)
                blacklists[curr_blacklist].append(_b_current_song)
                    
                
                if not silent:
                    warnings.append(Warning(f"song was {sanitize(_b_current_song)}", (40, con.HEIGHT-80, con.WIDTH-80), "info"))
                a = True
                while a:    
                    _b_song_counter += 1
                    # print("song counter", _b_song_counter, "_b_queue: ", _b_queue)
                    if _b_song_counter > len(_b_queue):
                        warnings.append(Warning(f"you finished the playlist!", (40, con.HEIGHT-80, con.WIDTH-80), "info"))
                        curr_screen = "playlists"
                        a = False
                    else:
                        # print("song counter", _b_song_counter)
                        _b_current_song = _b_queue[_b_song_counter - 1]
                        if Path(con.STEMS_FOLDER / _b_current_song).is_dir():
                            player.load(_b_current_song)
                            a = False
                        else:
                            warnings.append(Warning(f"couldnt find song folder", (40, con.HEIGHT-80, con.WIDTH-80), "warning"))
                            a = False
                            # print(f'{con.STEMS_FOLDER + "/" +  _b_current_song} is not a folder, it is possible the script failed to prepare mp3s yet')


    def setup():
        
        # GUI SPECIFIC CONSTANTS
        global SHADOW_OFFSET
        SHADOW_OFFSET = 10

        # GUI specific vars
        global loading_anim_slider
        loading_anim_slider = 0
        global go_back_button
        go_back_button = Button(19, 23, 101, 48, con.COLOR_PALETTE["red accent"], "Back", radius=15)
        global _mb_wiki_bool
        _mb_wiki_bool = True

        # preparing data for rest of script
        global all_songs_sorted
        global all_songs_sanitized_availability

        all_songs_sorted = all_songs[:]
        all_songs_sorted.sort()
        all_songs_sanitized_availability = []
        for i in range(len(all_songs_sorted)):
            if con.SONGS_JSON_DIR_contents[all_songs_sorted[i]]["status"] == "analysed":
                all_songs_sanitized_availability.append(True)
            else:
                all_songs_sanitized_availability.append(False)

        # sending to main menu intro
        global submenu
        global curr_screen
        submenu = "setup"
        curr_screen = "main_menu"

    def main_menu():
        global submenu

        # vars
        global curr_screen
        global loading_anim_slider
        
        # internal vars, sprites and data
        global _mm_y_spring_slider_anim
        global _mm_x_spring_slider_anim
        global _mm_y_spring_slider
        global _mm_x_spring_slider
        
        global _mm_settings_button
        global _mm_library_button
        global _mm_manage_blacklist_button
        global _mm_open_console_button
        global _mm_search_button 

        global _mm_CHEAT_MODE_toggle
        global _mm_global_suggestions_toggle

        global _mm_ANIM_SPEED
        _mm_ANIM_SPEED = 1/5



        if submenu == "setup":
            # prep for main menu + settings screen

            # sprites (mostly x=0 cuz its overwritten anyways)
            _mm_settings_button             = Button(0, 41 , 69, 50, con.COLOR_PALETTE["background"], "", radius=20)
            _mm_search_button               = Button(0, 360, 329, 115,  con.COLOR_PALETTE["face"], "Search", radius=20)
            _mm_library_button              = Button(0, 530 , 329, 115, con.COLOR_PALETTE["face"], "Library", radius=20)
            _mm_manage_blacklist_button     = Button(0, 508, 229, 82,  con.COLOR_PALETTE["face"], "Select\nblacklist", radius=20)
            _mm_open_console_button         = Button(0, 782, 229, 82,  con.COLOR_PALETTE["face"], "Open\nConsole", radius=20)

            _mm_CHEAT_MODE_toggle =         Toggle(0, 262)
            _mm_global_suggestions_toggle = Toggle(0, 384, default=True)

            # internal vars
            _mm_y_spring_slider_anim = False
            _mm_x_spring_slider_anim = False
            _mm_y_spring_slider = 0
            _mm_x_spring_slider = 0

            submenu = "intro"


        if submenu in ["settings", "main_menu", "intro", "loading_main_menu"]:
            # intro title and y slider
            if submenu == "intro":
                text_surface = con.title_font.render("Bandle", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH/2, con.HEIGHT/2-_mm_y_spring_slider*(con.HEIGHT/2 - 155)))
                screen.blit(text_surface, text_rect)

                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        _mm_y_spring_slider_anim = True

                if _mm_y_spring_slider_anim:
                    _mm_y_spring_slider += (1-_mm_y_spring_slider) * _mm_ANIM_SPEED

                if abs(_mm_y_spring_slider - 1) * 1000 < 1:
                    submenu = "main_menu"

            # y pos updates (only for main menu cuz y not)
            _mm_search_button.y           = 360    + con.HEIGHT*(1-_mm_y_spring_slider)
            _mm_library_button.y          = 530    + con.HEIGHT*(1-_mm_y_spring_slider)


            _mm_settings_button.x = 35 + _mm_x_spring_slider*360
            _mm_settings_button.y = 41 - (1-_mm_y_spring_slider)*100


            _mm_settings_button.draw(screen)
            if _mm_settings_button.is_clicked(events) == 1 and submenu != "intro":
                _mm_x_spring_slider_anim = True

            if _mm_x_spring_slider_anim:
                t = 0 if submenu == "settings" else 1
                _mm_x_spring_slider += (t-_mm_x_spring_slider)*_mm_ANIM_SPEED
                if abs((t-_mm_x_spring_slider) * 100) < 1:    
                    _mm_x_spring_slider_anim = False
                    submenu = "main_menu" if submenu == "settings" else "settings"

            if submenu != "intro":
                #Title text (Bandle)
                text_surface = con.title_font.render("Bandle", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH/2 + _mm_x_spring_slider*con.WIDTH, 155))
                screen.blit(text_surface, text_rect)
            #Title text (Settings)
            text_surface = con.title_font.render("Settings", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-con.WIDTH/2 + _mm_x_spring_slider*con.WIDTH, 155))
            screen.blit(text_surface, text_rect)
            #Title text (Dev Tools)
            text_surface = con.title_font.render("Dev Tools", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-con.WIDTH/2 + _mm_x_spring_slider*con.WIDTH, 685))
            screen.blit(text_surface, text_rect)
            #Toggle text (Cheat mode)
            text_surface = con.basic_font.render("Cheat Mode", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 274.5))
            screen.blit(text_surface, text_rect)
            #Toggle text (Global Suggestions)
            text_surface = con.basic_font.render("Global", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 380))
            screen.blit(text_surface, text_rect)
            text_surface = con.basic_font.render("Suggestions", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 410))
            screen.blit(text_surface, text_rect)



            _mm_search_button.x           = 85    + con.WIDTH*_mm_x_spring_slider
            _mm_library_button.x          = 85    + con.WIDTH*_mm_x_spring_slider
            _mm_manage_blacklist_button.x = -448  + con.WIDTH*_mm_x_spring_slider
            _mm_open_console_button.x     = -448  + con.WIDTH*_mm_x_spring_slider

            _mm_CHEAT_MODE_toggle.x       = -448  + con.WIDTH*_mm_x_spring_slider
            _mm_global_suggestions_toggle.x = -448  + con.WIDTH*_mm_x_spring_slider

            # all shadows
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(_mm_search_button.x + SHADOW_OFFSET           , _mm_search_button.y + SHADOW_OFFSET + (1-_mm_y_spring_slider)*con.HEIGHT, _mm_search_button.w, _mm_search_button.h), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(_mm_library_button.x + SHADOW_OFFSET          , _mm_library_button.y + SHADOW_OFFSET + (1-_mm_y_spring_slider)*con.HEIGHT, _mm_library_button.w, _mm_library_button.h), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(_mm_manage_blacklist_button.x + SHADOW_OFFSET , _mm_manage_blacklist_button.y + SHADOW_OFFSET + (1-_mm_y_spring_slider)*con.HEIGHT, _mm_manage_blacklist_button.w, _mm_manage_blacklist_button.h), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(_mm_open_console_button.x + SHADOW_OFFSET     , _mm_open_console_button.y + SHADOW_OFFSET + (1-_mm_y_spring_slider)*con.HEIGHT, _mm_open_console_button.w, _mm_open_console_button.h), border_radius=20)

            # settings tab icon
            pygame.draw.rect(screen, con.COLOR_PALETTE["list item unselected"], pygame.Rect(_mm_settings_button.x, _mm_settings_button.y, _mm_settings_button.w, 14), border_radius=5)
            pygame.draw.rect(screen, con.COLOR_PALETTE["list item unselected"], pygame.Rect(_mm_settings_button.x + _mm_x_spring_slider*15, _mm_settings_button.y + 18, 54, 14), border_radius=5)
            pygame.draw.rect(screen, con.COLOR_PALETTE["list item unselected"], pygame.Rect(_mm_settings_button.x + _mm_x_spring_slider*41, _mm_settings_button.y + 36, 28, 14), border_radius=5)


            _mm_search_button.draw(screen)
            _mm_manage_blacklist_button.draw(screen)
            _mm_open_console_button.draw(screen)
            _mm_library_button.draw(screen)

            _mm_CHEAT_MODE_toggle.draw(screen, events)
            con.CHEAT_MODE = _mm_CHEAT_MODE_toggle.state

            _mm_global_suggestions_toggle.draw(screen, events)
            con.GLOBAL_SUGGESTIONS =_mm_global_suggestions_toggle.state

            if _mm_library_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_library"
            if _mm_manage_blacklist_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_blacklists"
            if _mm_open_console_button.is_clicked(events):
                loading_anim_slider = 0
                # submenu = "loading_blacklists"  # need to add console
            if _mm_search_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_search"

            if submenu == "loading_main_menu":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "main_menu"
                    loading_anim_slider = 0
            

        if submenu in ["loading_library", "loading_blacklists", "loading_search"]:
            loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
            pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
            text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
            screen.blit(text_surface, text_rect)


            if abs((1-loading_anim_slider) * 100) < 1:
                if submenu == "loading_search":
                    submenu = "setup"
                    curr_screen = "select_song_setup"
                elif submenu == "loading_blacklists":
                    curr_screen = "manage_blacklist_setup"
                elif submenu == "loading_library":
                    curr_screen = "playlists_setup"

                loading_anim_slider = 0


    def manage_blacklist_setup():
        global submenu
        global curr_screen
        submenu = "setup"
        curr_screen = "manage_blacklist"
        
    def manage_blacklist():
        global submenu
        global curr_screen

        # vars
        global go_back_button
        global curr_blacklist
        global loading_anim_slider

        # internal vars
        global _mb_wiki
        global _mb_wiki_bool
        global _mb_wiki_slider
        global _mb_ANIM_SPEED
        _mb_ANIM_SPEED = 1/5

        global _mb_close_button
        global _mb_blacklist_buttons
        global _mb_name_edit

        global _mb_modify_button
        global _mb_add_button
        global _mb_delete_button

        if submenu == "setup":
            
            
            _mb_close_button  = Button(388, 232, 50, 50, con.COLOR_PALETTE["list item unselected"], "ok", 15)
            _mb_modify_button = Button(85, 790, 204, 52, con.COLOR_PALETTE["list item unselected"], "Modify", 15)
            _mb_add_button    = Button(300, 790, 52, 52, con.COLOR_PALETTE["list item unselected"], "+", 15)
            _mb_delete_button = Button(363, 790, 52, 52, con.COLOR_PALETTE["list item unselected"], "d", 15)

            
            _mb_blacklist_buttons = []
            for i in range(len(blacklist_names)):
                _mb_blacklist_buttons.append(Button(71, 536 + i*61, 358, 51, con.COLOR_PALETTE["list item unselected"], blacklist_names[i], 15))

            _mb_wiki = []
            _mb_wiki.append("The selected blacklist will")
            _mb_wiki.append("remember the songs you")
            _mb_wiki.append("played so you dont get them")
            _mb_wiki.append("twice.")
            _mb_wiki.append("Manage them as you wish!")
            _mb_wiki.append("you can also directly edit")
            _mb_wiki.append("\"Blacklists.txt\" for more control")

            if _mb_wiki_bool:
                _mb_wiki_slider = 1
            else:
                _mb_wiki_slider = 0

            _mb_name_edit = Textinput(86, con.HEIGHT, 330, 53, 15, con.COLOR_PALETTE["textinput unselected"])

            loading_anim_slider = 0
            submenu = "loading_manage_blacklists"
        
        if submenu in ["manage_blacklists", "loading_manage_blacklists", "loading_main_menu"]:

            # banner
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))

            #Title text (Bandle)
            text_surface = con.title_font.render("Select Blacklist", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(con.WIDTH/2, 155))
            screen.blit(text_surface, text_rect)

            # wiki
            if _mb_wiki_bool:
                pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(56 + SHADOW_OFFSET, 227 + SHADOW_OFFSET, 387, 265), border_radius=20)
                pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(56, 227, 387, 265), border_radius=20)
                for i in range(len(_mb_wiki)):
                    screen.blit(con.small_font.render(_mb_wiki[i], True, con.COLOR_PALETTE["black"]), (70, 227 + 20 + 30*i))

                _mb_close_button.draw(screen)

                if _mb_close_button.is_clicked(events):
                    _mb_wiki_bool = False

            # handling sliders
            if not _mb_wiki_bool:
                _mb_wiki_slider -= _mb_wiki_slider*_mb_ANIM_SPEED
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(56 + SHADOW_OFFSET, (_mb_wiki_slider * 293) + 227 + SHADOW_OFFSET   , 387, 346), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"]  , pygame.Rect(56                , (_mb_wiki_slider * 293) + 227                   , 387, 346), border_radius=20)

            for i in range(len(_mb_blacklist_buttons)):
                _mb_blacklist_buttons[i].y = i*61 + 243 + (_mb_wiki_slider * 293)
                if _mb_blacklist_buttons[i].is_clicked(events):
                    curr_blacklist = i
                if curr_blacklist == i:
                    _mb_blacklist_buttons[i].color = con.COLOR_PALETTE["list item selected"]
                else:
                    _mb_blacklist_buttons[i].color = con.COLOR_PALETTE["list item unselected"]
                _mb_blacklist_buttons[i].draw(screen)


            go_back_button.draw(screen)
            if go_back_button.is_clicked(events) == 1:
                submenu = "loading_main_menu"
                


            # edit blacklist island
            #Title text (Edit Blacklist)
            text_surface = con.basic_font.render("Edit Blacklist", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(con.WIDTH/2, 638 + _mb_wiki_slider * 400))
            screen.blit(text_surface, text_rect)

            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(56 + SHADOW_OFFSET, 668 + SHADOW_OFFSET + _mb_wiki_slider * 600, 387, 201), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(56, 668 + _mb_wiki_slider * 500, 387, 201), border_radius=20)

            # Text (Name)
            text_surface = con.small_font.render("Name", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (85, 685 + _mb_wiki_slider * 700))

            # Textinput
            if _mb_name_edit.focused == False:
                _mb_name_edit.text = blacklist_names[curr_blacklist]
            else:
                for event in  events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # editing blacklist name
                        if not _mb_name_edit.text in blacklist_names and _mb_name_edit.text != "":
                            blacklist_names[curr_blacklist] = _mb_name_edit.text
                            _mb_blacklist_buttons[curr_blacklist].text = _mb_name_edit.text

                            with open(con.BLACKLISTS_DIR, "r") as f:
                                a = f.read()
                            lines = a.splitlines()
                            lines[curr_blacklist] = _mb_name_edit.text + "=" + lines[curr_blacklist].split("=")[1]
                            b = "\n".join(lines)
                            with open(con.BLACKLISTS_DIR, "w") as f:
                                f.write(b)


            _mb_name_edit.y = 727 + _mb_wiki_slider*800
            _mb_name_edit.draw(screen, events)

            # buttons
            _mb_modify_button.y = 790 + _mb_wiki_slider*900
            _mb_add_button.y    = 790 + _mb_wiki_slider*900
            _mb_delete_button.y = 790 + _mb_wiki_slider*900

            _mb_modify_button.draw(screen)
            _mb_add_button.draw(screen)
            _mb_delete_button.draw(screen)

            if _mb_add_button.is_clicked(events):
                
                # writing changes to Blacklists.txt
                with open(con.BLACKLISTS_DIR, "r") as f:
                    a = f.read()
                lines = a.splitlines()

                # removing any empty lines that would mess things up
                bfr = []
                for i in range(len(lines)):
                    if lines[i] == "":
                        bfr.append(i)
                for i in range(len(bfr)):
                    lines.pop(bfr[i] - i)

                i = 0
                while True:
                    if not "new_blacklist_" + str(i) in blacklist_names:
                        break
                    i += 1
                n = f"new_blacklist_{i}"
                lines.append(n + "=")
                b = "\n".join(lines)
                with open(con.BLACKLISTS_DIR, "w") as f:
                    f.write(b)

                _mb_blacklist_buttons.append(Button(71, 536 + len(blacklist_names)*61, con.WIDTH-140, 60, con.COLOR_PALETTE["list item unselected"], n, 15))
                blacklist_names.append(n)
                blacklists.append([])

            if _mb_delete_button.is_clicked(events):
                if not len(blacklists) < 2:

                    # writing changes to Blacklists.txt
                    with open(con.BLACKLISTS_DIR, "r") as f:
                        a = f.read()
                    lines = a.splitlines()

                    # removing any empty lines that would mess things up
                    bfr = []
                    for i in range(len(lines)):
                        if lines[i] == "":
                            bfr.append(i)
                    for i in range(len(bfr)):
                        lines.pop(bfr[i] - i)


                    lines.pop(curr_blacklist)
                    b = "\n".join(lines)
                    with open(con.BLACKLISTS_DIR, "w") as f:
                        f.write(b)

                    _mb_blacklist_buttons.pop(curr_blacklist)
                    blacklist_names.pop(curr_blacklist)
                    blacklists.pop(curr_blacklist)
                    if curr_blacklist > len(blacklist_names)-1:
                        curr_blacklist -= 1 


    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if submenu == "loading_manage_blacklists":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "manage_blacklists"
                    loading_anim_slider = 0


            if submenu in ["loading_main_menu"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)


                if abs((1-loading_anim_slider) * 100) < 1:
                    if submenu == "loading_main_menu":
                        loading_anim_slider = 0
                        submenu = "loading_main_menu"
                        curr_screen = "main_menu"


    def select_song_setup():
        global submenu
        global curr_screen
        submenu = "setup"
        curr_screen = "select_song"

    def select_song():
        global submenu
        global curr_screen
        global _b_current_song
        global go_back_button
        global loading_anim_slider

        # local vars
        global _ss_library_button
        global _ss_global_search_button
        global _ss_categories
        global _ss_select_song_button
        global _ss_textinput

        global _ss_scrollpos
        global _ss_scrollvel
        global _ss_selected
        global _ss_pixelpositions


        if submenu == "setup":

            _ss_selected = -1
            _ss_scrollpos = 0
            _ss_scrollvel = 0

            _ss_library_button =            Button(0, con.HEIGHT-100, con.WIDTH/2, 100, con.COLOR_PALETTE["list item unselected"], "")
            _ss_global_search_button =      Button(con.WIDTH/2, con.HEIGHT-100, con.WIDTH/2, 100, con.COLOR_PALETTE["face"], "")
            _ss_select_song_button =        Button(20,700, con.WIDTH, 35, con.COLOR_PALETTE["face"], "", radius=10)
            _ss_textinput =                 Textinput(50, 160, con.WIDTH - 100, 50, 5, con.COLOR_PALETTE["textinput unselected"])

            _ss_categories = []
            for i in range(len(con.CATEGORIES)):
                _ss_categories.append(Button(81 + (i%2)*(178), 389 + math.floor(i/2)*87, 160, 70, con.COLOR_PALETTE["list item selected"], con.CATEGORIES[i], radius=15))

            _ss_pixelpositions = [i.y for i in _ss_categories]
            loading_anim_slider = 0
            submenu = "loading_search"


        if submenu in ["search", "loading_search", "loading_main_menu", "loading_bandle"]:
            
            # preparing listed song options
            text = _ss_textinput.text
            selection = []
            for i in all_songs_sorted:
                if text.lower() in sanitize(i).lower():
                    selection.append(i)
                elif text.lower() in con.SONGS_JSON_DIR_contents[i]["baked_artists"]:
                    selection.append(i)
            
            # updating scroll      
            _ss_scrollvel = (_ss_scrollvel + mouse_scroll*5)/2
            _ss_scrollpos = _ss_scrollpos + _ss_scrollvel*10
            if _ss_scrollpos < len(selection) * -38 + 106:
                _ss_scrollpos = len(selection) * -38 + 106
            if _ss_scrollpos > 0:
                _ss_scrollpos = 0

            # placing a button under the cursor if hovering on the options
            if mouse_y > 725 + _ss_scrollpos and mouse_y < con.HEIGHT-106:
                _ss_selected = math.floor((mouse_y-725-_ss_scrollpos)/38)
                _ss_select_song_button.y = math.floor((mouse_y-725-_ss_scrollpos)/38) * 38 + 725 + _ss_scrollpos
                if _ss_selected < len(selection):
                    _ss_select_song_button.draw(screen)
                    if _ss_select_song_button.is_clicked(events):
                        if all_songs_sanitized_availability[all_songs_sorted.index(selection[_ss_selected])] == False:
                            warnings.append( Warning("this song isnt available", (40, con.HEIGHT-80, con.WIDTH-80), level="warning"))
                        else:
                            print("selected: ", all_songs[all_songs.index(selection[_ss_selected])])
                            _b_current_song = all_songs[all_songs.index(selection[_ss_selected])]
                            print("curr_song: ", _b_current_song)
                            submenu = "loading_bandle"

            # render options text
            for i in range(len(selection)):
                if 725 + _ss_scrollpos + i*38 > 0 and 725 + _ss_scrollpos + i*38 < con.HEIGHT:
                    text_surface = con.small_font.render(sanitize(selection[i]), True, con.COLOR_PALETTE["black"])
                    if all_songs_sanitized_availability[all_songs_sorted.index(selection[i])] == False:
                        text_surface = con.small_font.render(sanitize(selection[i]), True, con.COLOR_PALETTE["list item unselected"])
                    screen.blit(text_surface, (40,725 + _ss_scrollpos + i*38))


            _ss_categories[0].y =        _ss_pixelpositions[0] + _ss_scrollpos
            _ss_categories[1].y =        _ss_pixelpositions[1] + _ss_scrollpos
            _ss_categories[2].y =        _ss_pixelpositions[2] + _ss_scrollpos
            _ss_categories[3].y =        _ss_pixelpositions[3] + _ss_scrollpos
            _ss_textinput.y = 176 + _ss_scrollpos if _ss_scrollpos > -43 else 133

            for i in _ss_categories:
                i.draw(screen)
            
            # Categories header
            text_surface = con.title_font.render("Categories", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (81,271 + _ss_scrollpos))
            # Songs header
            text_surface = con.title_font.render("Songs", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (81,600 + _ss_scrollpos))
            
            # Library and Search buttons
            _ss_library_button.draw(screen)
            _ss_global_search_button.draw(screen)

            # banner
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))
            text_surface = con.small_font.render("Search" if submenu in ["search", "loading_search", "loading_main_menu"] else "Your Library" if submenu == "library" else "", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (con.WIDTH/2 + 55 - text_surface.get_width()/2,20 + go_back_button.h/2 - 18))

            go_back_button.draw(screen)
            if go_back_button.is_clicked(events) == 1:
                submenu = "loading_main_menu"

            _ss_textinput.draw(screen, events)

    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if submenu == "loading_search":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "search"
                    loading_anim_slider = 0


            if submenu in ["loading_main_menu", "loading_bandle"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)


                if abs((1-loading_anim_slider) * 100) < 1:
                    if submenu == "loading_main_menu":
                        loading_anim_slider = 0
                        submenu = "loading_main_menu"
                        curr_screen = "main_menu"
                    elif submenu == "loading_bandle":
                        loading_anim_slider = 0
                        submenu = "setup_song"
                        curr_screen = "bandle_setup"


    def playlist_select_setup():
        global submenu
        global curr_screen
        submenu = "setup"
        curr_screen = "playlists"

    def playlist_select():
        global submenu
        global curr_screen
        global loading_anim_slider

        global selected_playlist

        global _ps_selected_playlist_idx
        global _ps_playlist_buttons
        global _ps_start_button
        global _ps_scrollpos
        global _ps_scrollvel

        
        if submenu == "setup":
            _ps_scrollpos, _ps_scrollvel = 0, 0
            _ps_selected_playlist_idx = -1
            _ps_playlist_buttons = []
            selected_playlist = ""
            
            _ps_start_button = Button(135, 774, 229, 92, con.COLOR_PALETTE["face"], "Start", radius=20, click_counter=20)


            for i in range(len(list(playlists_json_dir_contents.keys()))):
                _ps_playlist_buttons.append(Button(86, 247 + i*62, 328, 52, con.COLOR_PALETTE["list item unselected"], playlists_json_dir_contents[list(playlists_json_dir_contents.keys())[i]]["name"], radius=15, info=list(playlists_json_dir_contents.keys())[i]))
            
            loading_anim_slider = 0
            submenu = "loading_main"

        
        if submenu in ["main", "loading_main", "out_loading_main_menu", "loading_bandle"]:
            if len(_ps_playlist_buttons) > 6:
                _ps_scrollvel = (_ps_scrollvel + mouse_scroll*3)/2
                _ps_scrollpos += _ps_scrollvel
                if _ps_scrollpos > 0:
                    _ps_scrollpos = 0
                elif _ps_scrollpos < -len(_ps_playlist_buttons)*6 + 37.5:
                    _ps_scrollpos = -len(_ps_playlist_buttons)*6 + 37.5
                _ps_scrollvel=round(_ps_scrollvel*10)/10
                _ps_scrollpos=round(_ps_scrollpos*100)/100
            else:
                _ps_scrollpos = 0
            
            # island
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(56 + SHADOW_OFFSET, 231 + SHADOW_OFFSET, 387, 412), border_radius=20)
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(56, 231, 387, 412), border_radius=20)

            # check who is selected
            for i in range(len(_ps_playlist_buttons)):
                if mouse_y > 230 and mouse_y < 619:
                    if _ps_playlist_buttons[i].is_clicked(events):
                        _ps_selected_playlist_idx = i
                        selected_playlist = _ps_playlist_buttons[i].info
            # draw buttons
            for i in range(len(_ps_playlist_buttons)):
                if i == _ps_selected_playlist_idx:
                    _ps_playlist_buttons[i].color = con.COLOR_PALETTE["list item selected"]
                else:
                    _ps_playlist_buttons[i].color = con.COLOR_PALETTE["list item unselected"]
                _ps_playlist_buttons[i].x, _ps_playlist_buttons[i].y = (86, 247 + i*62 + _ps_scrollpos*10)
                _ps_playlist_buttons[i].draw(screen)

            # hacky caches for the buttons
            pygame.draw.rect(screen, con.COLOR_PALETTE["background"], pygame.Rect(0, 0, con.WIDTH, 231))
            pygame.draw.rect(screen, con.COLOR_PALETTE["background"], pygame.Rect(0, 643 + SHADOW_OFFSET, con.WIDTH, 400))
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(86, 643, 328, SHADOW_OFFSET), border_radius=-1)


            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))
            text_surface = con.small_font.render("Select playlist", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (con.WIDTH/2 + 55 - text_surface.get_width()/2,20 + go_back_button.h/2 - 18))

            go_back_button.draw(screen)
            if go_back_button.is_clicked(events) == 1:
                submenu = "out_loading_main_menu"

            # title text
            text_surface = con.title_font.render("Select playlist", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (con.WIDTH/2 - text_surface.get_width()/2,120))

        
            
            pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(_ps_start_button.x + SHADOW_OFFSET, _ps_start_button.y + SHADOW_OFFSET, _ps_start_button.w, _ps_start_button.h), border_radius=20)
            _ps_start_button.draw(screen)

            if _ps_start_button.is_clicked(events) == 1:  
                if selected_playlist != "":
                    submenu = "loading_bandle"
                else:
                    warnings.append( Warning("you need to select a playlist", (40, con.HEIGHT-80, con.WIDTH-80), level="warning"))


    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if submenu == "loading_main":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "main"
                    loading_anim_slider = 0

            if submenu in ["out_loading_main_menu", "loading_bandle"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if submenu == "out_loading_main_menu":
                    if abs((1-loading_anim_slider) * 100) < 1:
                        submenu = "loading_main_menu"
                        curr_screen = "main_menu"
                        loading_anim_slider = 0
                elif submenu == "loading_bandle":
                    if abs((1-loading_anim_slider) * 100) < 1:
                        submenu = "setup_playlist"
                        curr_screen = "bandle_setup"
                        loading_anim_slider = 0
                        


    def bandle_setup():
        global submenu
        global curr_screen
        global loading_anim_slider

        # bandle screen vars
        global _b_loading_status
        global _b_current_song
        global _b_song_counter
        global _b_queue
        global _b_step
        global _b_bandle_guessing_counter
        global _b_single_song_bool
        global text
        global selected
        global offset
        global seeking

        global _b_skip_button
        global _b_play_button
        global _b_guess_button
        global _b_skip_ahead
        global _b_skip_ahead_img
        global _b_rewind
        global _b_rewind_img
        global textinput

        global player

        # setting vars
        _b_step = 1
        _b_song_counter = 1
        _b_bandle_guessing_counter = 0
        text = ""
        selected = -1
        offset = 0
        seeking = False

        # setting buttons
        _b_play_button  = Button(213 , 750, 75 , 65 , con.COLOR_PALETTE["list item selected"], ">"      , radius=15, click_counter=20)
        _b_skip_button  = Button(388, 741, 95 , 83 , con.COLOR_PALETTE["list item selected"], "Skip"      , radius=15, click_counter=20)
        _b_guess_button = Button(16 , 741, 95 , 83 , con.COLOR_PALETTE["list item selected"], "Guess", radius=15, click_counter=20)

        _b_rewind =     Button(con.WIDTH/2 - 45 -90  , con.HEIGHT -210, 90 , 85 , con.COLOR_PALETTE["background"], ""      , radius=20, click_counter=20)
        _b_skip_ahead = Button(con.WIDTH/2 + 45      , con.HEIGHT -210, 90 , 85 , con.COLOR_PALETTE["background"], ""      , radius=20, click_counter=20)
        
        _b_skip_ahead_img = pygame.image.load(con.ASSETS_DIR / "skip_ahead.png").convert_alpha()
        _b_skip_ahead_img = pygame.transform.smoothscale(_b_skip_ahead_img, (60, 60))

        _b_rewind_img = pygame.image.load(con.ASSETS_DIR / "rewind.png").convert_alpha()
        _b_rewind_img = pygame.transform.smoothscale(_b_rewind_img, (60, 60))

        textinput = Textinput(25, con.HEIGHT, con.WIDTH-50, 60, 20, con.COLOR_PALETTE["textinput unselected"])



        if submenu == "setup_song":
            _b_single_song_bool = True
            # preparing song _b_queue
            _b_queue = [_b_current_song]
            player.load(_b_current_song)
            player.seek(player.audio_len / 5, step=1)


        elif submenu == "setup_playlist":
            _b_single_song_bool = False
            # preparing song _b_queue
            # all songs in a playlist
            _b_queue = [playlists_json_dir_contents[selected_playlist]["data"][i]["name"] for i in range(len(playlists_json_dir_contents[selected_playlist]["data"]))]
            # removing ones that havent been fully processed yet
            bfr = []
            for i in range(len(_b_queue)):
                if all_songs_sanitized_availability[all_songs_sorted.index(_b_queue[i])] == False:
                    bfr.append(i)
            for i in range(len(bfr)):
                _b_queue.pop(bfr[i] - i)
            # removing ones encountered in active blacklist
            bfr = []
            for i in range(len(_b_queue)):
                if _b_queue[i] in blacklists[curr_blacklist]:
                    bfr.append(i)
            for i in range(len(bfr)):
                _b_queue.pop(bfr[i] - i)

        
        # check if there's anything left
        if _b_queue == []:
            curr_screen = "playlists"
            submenu = "main"
            warnings.append( Warning("already finished this playlist", (40, con.HEIGHT-80, con.WIDTH-80), level="warning"))
        else:

            if submenu == "setup_playlist":
                shuffle(_b_queue)
                _b_current_song = _b_queue[0]
                player.load(_b_current_song)
                player.seek(player.audio_len / 5, step=1)
            
            loading_anim_slider = 0
            _b_loading_status = "loading_in"
            submenu = "bandle"
            curr_screen = "bandle"
        
    def bandle_screen():
        global submenu
        global curr_screen
        global loading_anim_slider

        global _b_loading_status
        global _b_step
        global _b_song_counter
        global _b_current_song
        global _b_bandle_guessing_counter
        global offset
        global selected

        global mouse_x
        global mouse_y
        global seeking

        global _b_skip_button
        global go_back_button
        global _b_play_button
        global _b_skip_ahead
        global _b_rewind
        global _b_skip_ahead_img
        global _b_rewind_img
        global textinput
        
        global player

        # submenu can have a whole range of values:
        # ["bandle"; "bandle_guessing"; "bandle_win"; "bandle_stare"]
        #
        # bandle is the default one, 
        # bandle_guessing means the guessing popup should appear, most actions are therefore prevented
        # bandle_win means the victory popup should appear, most actions are therefore prevented
        # bandle stare is a special restricted mode in which you cant guess, can only skip to next track (instead of stem) and clicking on a stem should enable/disable it
        #
        # _b_single_song_bool is also important: if True, _b_queue isnt defined, and after finishing the stems, you should directly go to select_songs
        #
        # each individual section will be marked by an adequate marker, ex:

    # ╭--------------------------------------------╮
    # |      ╭=-  ╭  ╮ ╭==╮ ╭╮╭╮ ╭==╮ ╭   ╭=-      |
    # |      ╞-    ><  ╞--╡ |╰╯| ╞==╯ |   ╞-       |
    # |      ╰=-  ╰  ╯ ╰  ╯ ╰  ╯ ╰    ╰-╯ ╰=-      |
    # ╰--------------------------------------------╯

        if submenu in ["bandle", "bandle_guessing", "bandle_win", "bandle_stare"]:
            #deal with players
            #MUTED OUTPUT  print("progression would be updated here")
            player.update_pointer()
            progression = player.pointer * 1000 / player.audio_len if player.audio_len != 0 else 0

        # ╭----------------------------------------╮
        # |      ╭  ╮ ╭=-  ╭==╮ ╭-.  ╭=- ╭==╮      |
        # |      ╞--╡ ╞-   ╞--╡ |  | ╞-  ╞=:╯      |
        # |      ╰  ╯ ╰=-  ╰  ╯ ╰='  ╰=- ╰  ╰      |
        # ╰----------------------------------------╯
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))

            # title text
            bandle_title = con.title_font.render("Bandle", True, con.COLOR_PALETTE["black"])
            screen.blit(bandle_title, (con.WIDTH/2 - bandle_title.get_width()/2,120))
            
            
            
            # selected playlist text (cool little script)
            if not _b_single_song_bool:
                selected_playlist_text = f"Selected playlist: {playlists_json_dir_contents[selected_playlist]['name']}"
            else:
                selected_playlist_text = f"testing single song"
            words = selected_playlist_text.split(" ")
            wordlines = []

            for i in range(len(words)):
                for j in range(len(words)):
                    # print(f"j: {j}, len of {str(words[:len(words) - j])} is {sum(len(words[i]) for i in range(len(words) - j))}")
                    if sum(len(words[i]) for i in range(len(words) - j)) < 25 or j == len(words) - 1:

                        selected_playlist_text = "".join((words[i] + " ") for i in (range(len(words) - j)))
                        selected_playlist_text = selected_playlist_text[:-1]
                        wordlines.append(selected_playlist_text)

                        for i in range(len(words[:len(words) - j])):
                            words.pop(0)
                        break
                # print(f"i: {i}, words: {words}")
                if words == []:
                    break
            
            for i in range(len(wordlines)):
                selected_playlist_text = con.small_font.render(wordlines[i], True, con.COLOR_PALETTE["black"])
                screen.blit(selected_playlist_text, (con.WIDTH/2 + 55 - selected_playlist_text.get_width()/2,20 + go_back_button.h/2 - 18 - (len(wordlines)-1)*30/2 + i*30))

            
            # cheat mode display
            if con.CHEAT_MODE:
                song_text = con.basic_font.render(f"Current song: {_b_current_song}, ya little CHEATER", True, con.COLOR_PALETTE["black"])
                screen.blit(song_text, (50, 200))


        # ╭----------------------------------╮
        # |      ╭==╮ ╭=╮ ╭=-  ╭╮╭╮ ╭==╮     |
        # |      ╰--╮  |  ╞-   |╰╯| ╰--╮     |
        # |      ╰==╯  ╰  ╰=-  ╰  ╯ ╰==╯     |
        # ╰----------------------------------╯
            # draw stem rectangles
            for i in range(len(con.STEMS)):
                
                if submenu == "bandle_stare":
                    
                    b = Button(71, 246 + i*74, 361, 60, con.COLOR_PALETTE["black"], f"{con.STEMS[i]}", 15)
                    
                    b.draw(screen)
                    if b.is_clicked(events):
                        _b_step = i
                        skip(True, simple_update=True)
                    # pygame.draw.rect(screen, (200, 200, 200) if i < _b_step else (150, 150, 150), pygame.Rect(50, 250 + i*80, con.WIDTH - 100, 60), border_radius=15)
                    # stem_text = con.basic_font.render(f"{con.STEMS[i]}", True, (10, 10 ,10))
                    # screen.blit(stem_text, (con.WIDTH/2 - stem_text.get_width()/2, 254 + i*80))



                # stems
                pygame.draw.rect(screen, con.COLOR_PALETTE["stems selected"] if i < _b_step else con.COLOR_PALETTE["face"], pygame.Rect(71, 246 + i*74, 361, 60), border_radius=15)
                

                # visualizer
                a = con.SONGS_JSON_DIR_contents[_b_current_song]["baked_diagnosis"][con.STEMS[i]].split("|")[1].split(";")
                s = con.SONGS_JSON_DIR_contents[_b_current_song]["baked_diagnosis"][con.STEMS[i]].split("|")[0]
                
                for j in range(len(a)):

                    if i < _b_step:
                        c = con.COLOR_PALETTE["list item selected"] if j < progression*len(a) else con.COLOR_PALETTE["black"]
                    else:
                        c = con.COLOR_PALETTE["list item unselected"] if j < progression*len(a) else con.COLOR_PALETTE["textinput selected"]

                    w = (float(a[j])*60*2 if float(a[j])<0.5 else 60)
                    pygame.draw.rect(screen, c, pygame.Rect(72 + 8*j, 310 - w +  74*i, 5, w), border_radius=5)


                pygame.draw.rect(screen, con.COLOR_PALETTE["background"], pygame.Rect(71 -7, 246 + i*74 -7, 361 +14, 60 +14), 7, border_radius=22)


                # text
                if s == "1":
                    stem_text = con.basic_font.render(f"{con.STEMS[i]}", True, con.COLOR_PALETTE["background"] if i < _b_step else con.COLOR_PALETTE["black"])
                else:
                    stem_text = con.basic_font.render(f"{con.STEMS[i]}", True, con.COLOR_PALETTE["shadow"] if i < _b_step else con.COLOR_PALETTE["list item unselected"])
                screen.blit(stem_text, (con.WIDTH/2 - stem_text.get_width()/2, 249 + i*76))

        # ╭------------------------------------------------------------------╮
        # |      ╭==╮ ╭  ╮ ╭=- ╭==╮ ╭==╮    ╭=-. ╭  ╮ ╭=╮ ╭=╮ ╭==╮ ╭╮ ╮      |
        # |      |  ╮ |  | ╞-  ╰--╮ ╰--╮    ╞-:╯ |  |  |   |  |  | |╰╮|      |
        # |      ╰==╯ ╰==╯ ╰=- ╰==╯ ╰==╯    ╰=-╯ ╰==╯  ╰   ╰  ╰==╯ ╰ ╰╯      |
        # ╰------------------------------------------------------------------╯
            # guess button
            if submenu != "bandle_stare":
                _b_guess_button.draw(screen)
                if _b_guess_button.is_clicked(events) == 1:
                    if submenu != "bandle_guessing":
                        submenu = "bandle_guessing"
                        offset = 0                      # shows the top of the possible options
                        selected = -1                   # unselects any option
                        _b_bandle_guessing_counter = 0     # sort of frame timer used for fade in
                        textinput.focused = True
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and submenu == "bandle_guessing":
                        if mouse_y < con.HEIGHT - 500:
                            submenu = "bandle"
            else:
                _b_guess_button.draw(screen, con.COLOR_PALETTE["face"])
                if _b_guess_button.is_clicked(events) == 1:
                    warnings.append(Warning("cannot guess in admire mode", level="warning"))
            

        # ╭-----------------------------------------------------------╮
        # |      ╭╮ ╮ ╭==╮  ╭   ╮  .  ╭==╮ ╭==╮ ╭=╮  .  ╭==╮ ╭╮ ╮     |
        # |      |╰╮| ╞--╡  '   '  |  |  ╮ ╞--╡  |   |  |  | |╰╮|     |
        # |      ╰ ╰╯ ╰  ╯   ╰=╯   ╰  ╰==╯ ╰  ╯  ╰   ╰  ╰==╯ ╰ ╰╯     |
        # ╰-----------------------------------------------------------╯
            # naviagtion
            _b_skip_ahead.draw(screen)
            if _b_skip_ahead.is_clicked(events):
                player.offset_player(5000)

            screen.blit(_b_skip_ahead_img, (con.WIDTH/2 + 90 -30  , con.HEIGHT -195))

            _b_rewind.draw(screen)
            if _b_rewind.is_clicked(events):
                player.offset_player(-5000)

            screen.blit(_b_rewind_img, (con.WIDTH/2 - 90 -30  , con.HEIGHT -195))

            # progression bar
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(121, 890, 260, 10), border_radius=5)
            pygame.draw.rect(screen, con.COLOR_PALETTE["list item selected"], pygame.Rect(121, 890, 10 + 250*progression, 10), border_radius=5)

            # progress bar hitbox visualizer
            # pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(con.WIDTH/2-120, 870, 240, 110))
            # pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(con.WIDTH/2+120, 870, 100, 110))
            # pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(con.WIDTH/2-220, 870, 100, 110))

            if pygame.mouse.get_pressed()[0]:
                if mouse_y > 870 and mouse_y < 870+110 and mouse_x > con.WIDTH/2-220 and mouse_x < con.WIDTH/2+220:
                    if mouse_x > con.WIDTH/2-130:
                        if mouse_x > con.WIDTH/2+130:
                            player.seek(player.audio_len)
                            seeking = True
                        else:
                            player.seek((mouse_x - (con.WIDTH/2-130))/260 * player.audio_len)
                            seeking = True
                    else:
                        player.seek(0)
                        seeking = True
            else:
                if seeking:
                    seeking = not seeking
            
            if seeking:
                if player.status == "Playing":
                    player.toggle()


        # ╭-------------------------------------------------------------------------╮
        # |      ╭==╮ ╭==╮   ╭=-. ╭==╮ ╭=-╮ ╭  ╭   ╭=-. ╭  ╮ ╭=╮ ╭=╮ ╭==╮ ╭╮ ╮      |
        # |      |  ╮ |  |   ╞=:╯ ╞--╡ |    ╞=:    ╞=:╯ |  |  |   |  |  | |╰╮|      |
        # |      ╰==╯ ╰==╯   ╰=-╯ ╰  ╯ ╰=-╯ ╰  ╰   ╰=-╯ ╰==╯  ╰   ╰  ╰==╯ ╰ ╰╯      |
        # ╰-------------------------------------------------------------------------╯
            # go back button
            go_back_button.draw(screen)
            if  submenu != "bandle_guessing":
                if go_back_button.is_clicked(events) == 1:
                    player.stop_all()
                    if not _b_single_song_bool:
                        _b_loading_status = "out_loading_playlist"
                    else:
                        _b_loading_status = "out_loading_song"

        # ╭------------------------------------------------------------╮
        # |      ╭==╮ ╭  ╭  .  ╭==╮   ╭=-. ╭  ╮ ╭=╮ ╭=╮ ╭==╮ ╭╮ ╮      |
        # |      ╰--╮ ╞=:   |  ╞==╯   ╞=:╯ |  |  |   |  |  | |╰╮|      |
        # |      ╰==╯ ╰  ╰  ╰  ╰      ╰=-╯ ╰==╯  ╰   ╰  ╰==╯ ╰ ╰╯      | 
        # ╰------------------------------------------------------------╯
            # skip button
            _b_skip_button.draw(screen)
            if submenu != "bandle_guessing":
                if _b_skip_button.is_clicked(events) == 1:
                    if _b_single_song_bool and _b_step == 6: # when in test single song mode, instead of skipping, you simply go back to select_song
                        _b_loading_status = "out_loading_song"
                    else:
                        # here, bandle_stare is the only mode that should both be silent (no warnings) and simple_update (no going back to the start of the song)
                        skip(True if submenu == "bandle_stare" else False, True if submenu == "bandle_stare" else False)
                    if _b_step == len(con.STEMS):
                        _b_skip_button.text = "End"
                    else:
                        _b_skip_button.text = "Skip"
                    if submenu in ["bandle", "bandle_guessing", "bandle_win", "bandle_stare"]: #if its not, an earlier part of the script tried to change screens, which shouldnt be overridden
                        submenu = "bandle"
                

        # ╭--------------------------------------------------------------------------------------╮
        # |      ╭==╮ ╭   ╭==╮ ╮ ╭   ╮╭==╮ ╭==╮ ╭  ╮ ╭==╮ ╭=-   ╭=-. ╭  ╮ ╭=╮ ╭=╮ ╭==╮ ╭╮ ╮      |
        # |      ╞==╯ |   ╞--╡ ╰╭╯ ╭╯ ╞==╯ ╞--╡ |  | ╰--╮ ╞-    ╞=:╯ |  |  |   |  |  | |╰╮|      |
        # |      ╰    ╰-╯ ╰  ╯  ╯ ╰   ╰    ╰  ╯ ╰==╯ ╰==╯ ╰=-   ╰=-╯ ╰==╯  ╰   ╰  ╰==╯ ╰ ╰╯      |
        # ╰--------------------------------------------------------------------------------------╯
            # play/pause button
            # make the button change depending on state
            #MUTED OUTPUT  print("check if playing to change play button appearance")
            if  player.status != "Playing":
                _b_play_button.text = "Play"
            else:
                _b_play_button.text = "Pause"
            _b_play_button.draw(screen)

            if submenu != "bandle_guessing":
                if _b_play_button.is_clicked(events) == 1:
                    player.curr_step = _b_step    
                    player.toggle()
                    # if not players[0].is_playing():
                    #     if players[0].get_time() >= players[0].get_length():
                    #         print("set_position(0)")
                    #         print("play_step()")
                    #     else:
                    #         print("play_step()")
                    # else:
                    #     print("pause()")
                    
            #MUTED OUTPUT  print("set_volume(_b_step)")

        # ╭----------------------------------------------------------------------------╮
        # |      ╭==╮ ╭  ╮ ╭=- ╭==╮ ╭==╮  .  ╭╮ ╮ ╭==╮   ╭==╮ ╭==╮ ╭==╮ ╭  ╮ ╭==╮      |
        # |      |  ╮ |  | ╞-  ╰--╮ ╰--╮  |  |╰╮| |  ╮   ╞==╯ |  | ╞==╯ |  | ╞==╯      |
        # |      ╰==╯ ╰==╯ ╰=- ╰==╯ ╰==╯  ╰  ╰ ╰╯ ╰==╯   ╰    ╰==╯ ╰    ╰==╯ ╰         |
        # ╰----------------------------------------------------------------------------╯
            # bandle guessing screen popup
            if submenu == "bandle_guessing":
                    
                # slight shade
                s = pygame.Surface((1000,1000))  
                s.set_alpha(_b_bandle_guessing_counter * 128)             
                s.fill(con.COLOR_PALETTE["background"])           
                screen.blit(s, (0,0))  

                #popup
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0, con.HEIGHT - (500/0.5)*_b_bandle_guessing_counter if _b_bandle_guessing_counter < 0.5 else con.HEIGHT - 500, con.WIDTH, 600), border_radius=20)
                
                textinput.y = con.HEIGHT + 30 - (500/0.5)*_b_bandle_guessing_counter if _b_bandle_guessing_counter < 0.5 else con.HEIGHT + 30 - 500
                textinput.draw(screen, events)
                

                limit = 10
                text = textinput.text
                suggestions = []
                actual_suggestions = []
                for i in range(len(all_songs_sanitized)):
                    if text.lower() in all_songs_sanitized[i].lower():
                        if all_songs_sanitized[i] not in suggestions:
                            suggestions.append(all_songs_sanitized[i])
                            actual_suggestions.append(all_songs[i])
                    elif text.lower() in con.SONGS_JSON_DIR_contents[all_songs_sanitized[i]]["baked_artists"]:
                        if all_songs_sanitized[i] not in suggestions:
                            suggestions.append(all_songs_sanitized[i])
                            actual_suggestions.append(all_songs[i])

                go_down = True if (k_down-20 > 0 and counter%4 == 0) or k_down == 1 else False
                go_up = True if (k_up-20 > 0 and counter%4 == 0) or k_up == 1 else False
                enter = 0
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        enter = True if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN else False
                        if event.key == pygame.K_ESCAPE:
                            submenu = "bandle"
                

                if textinput.focused:
                    if enter or go_down:
                        textinput.focused = False
                        selected = 0
                else:
                    if go_down:
                        selected += 1
                    if go_up:
                        selected -= 1
                    if enter:
                        #guess
                        guess = actual_suggestions[selected]
                        # print(f"you guessed: {guess}, correct would be {_b_current_song}")
                        if guess == _b_current_song:
                            submenu = "bandle_win"
                        else: 
                            warnings.append(Warning("nope", (40, con.HEIGHT-80, con.WIDTH-80), "info"))
                            skip()
                            submenu = "bandle"


                if selected > len(suggestions) - 1:
                    selected = len(suggestions) - 1
                elif selected < 0:
                    selected = -1
                    textinput.focused = True
            

                if selected >  offset + limit - 2:
                    offset += 1
                elif selected < offset+1:
                    offset -= 1
                
                if offset < 0:
                    offset = 0
                elif offset > len(suggestions)  - limit:
                    offset = (len(suggestions)  - limit) if (len(suggestions) - limit) > 0 else 0
                    
                suggestions = suggestions[offset:offset + limit]
                

                if selected != -1:
                    pygame.draw.rect(screen, con.COLOR_PALETTE["list item selected"], pygame.Rect(10, 560 + (selected-offset)*40, con.WIDTH-20, 30), border_radius=5)

                for i in suggestions:
                    suggestion_surf = con.basic_font.render(i, True, con.COLOR_PALETTE["black"])
                    screen.blit(suggestion_surf, (50, con.HEIGHT + 100 + suggestions.index(i)*40 - (500/0.5)*_b_bandle_guessing_counter if _b_bandle_guessing_counter < 0.5 else con.HEIGHT + 100 + suggestions.index(i)*40 - 500))

                _b_bandle_guessing_counter += 1/30
                if _b_bandle_guessing_counter > 1:
                    _b_bandle_guessing_counter = 1

        # ╭-----------------------------------------------------------------------╮
        # |      ╭   ╮  .  ╭=-╮ ╭=╮ ╭==╮ ╭==╮ ╮ ╭    ╭==╮ ╭==╮ ╭==╮ ╭  ╮ ╭==╮     |
        # |      '   '  |  |     |  |  | ╞=:╯ ╰╮╯    ╞==╯ |  | ╞==╯ |  | ╞==╯     |
        # |       ╰=╯   ╰  ╰=-╯  ╰  ╰==╯ ╰  ╰  ╯     ╰    ╰==╯ ╰    ╰==╯ ╰        |
        # ╰-----------------------------------------------------------------------╯
            # big victory popup
            if submenu == "bandle_win":
                
                s = pygame.Surface((1000,1000))  
                s.set_alpha(_b_bandle_guessing_counter * 128)             
                s.fill(con.COLOR_PALETTE["background"])           
                screen.blit(s, (0,0)) 

                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH/2-225, con.HEIGHT/2 -225, 450, 450), border_radius=20)
                win_text = con.title_font.render("YOU WON", True, con.COLOR_PALETTE["black"])
                screen.blit(win_text, (con.WIDTH/2 - win_text.get_width()/2, con.HEIGHT/2 - 200))

                if not _b_single_song_bool:
                    butt = Button(con.WIDTH/2-150, con.HEIGHT/2-50, 300, 100, con.COLOR_PALETTE["list item selected"], "go back and admire", 20)
                    butt.draw(screen)
                    if butt.is_clicked(events):
                        submenu = "bandle_stare"
                    
                    next = Button(con.WIDTH/2-150, con.HEIGHT/2+100, 300, 100, con.COLOR_PALETTE["list item selected"], "go next", 20)
                    next.draw(screen)
                    if next.is_clicked(events):
                        skip(True, True)
                        submenu = "bandle"
                else:
                    next = Button(con.WIDTH/2-150, con.HEIGHT/2-50, 300, 100, con.COLOR_PALETTE["list item selected"], "Return to selection", 20)
                    next.draw(screen)
                    if next.is_clicked(events):
                        player.stop_all()
                        _b_loading_status = "out_loading_song"



    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if _b_loading_status == "loading_in":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "bandle"
                    loading_anim_slider = 0
                    _b_loading_status = "nope"

            if _b_loading_status in ["out_loading_playlist", "out_loading_song"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, (10, 10 ,10))
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if _b_loading_status == "out_loading_playlist":
                    if abs((1-loading_anim_slider) * 100) < 1:
                        submenu = "loading_main"
                        curr_screen = "playlists"
                        loading_anim_slider = 0
                elif _b_loading_status == "out_loading_song":
                    if abs((1-loading_anim_slider) * 100) < 1:
                        submenu = "loading_search"
                        curr_screen = "select_song"
                        loading_anim_slider = 0
                        




    global curr_screen
    global warnings
    global counter
    counter = 0
    curr_screen = "setup"
    warnings = []

    con.logger.pretty_text("opening Graphical Interface, a window should pop up right about now...", "magenta")
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        screen.fill(con.COLOR_PALETTE["background"])  # fill screen with pink

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        mouse_scroll = 0
        key_scroll = 0
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                event.pos = scale_mouse_pos(event.pos)
                mouse_x, mouse_y = event.pos[:]
            if event.type == pygame.MOUSEWHEEL:
                mouse_scroll = event.y

        
        if keys[pygame.K_DOWN]:
            k_down += 1
        else:
            k_down = 0
        if keys[pygame.K_UP]:
            k_up += 1
        else:
            k_up = 0

        if curr_screen == "setup":
            setup()
        elif curr_screen == "main_menu":
            main_menu()
        elif curr_screen == "manage_blacklist_setup":
            manage_blacklist_setup()
        elif curr_screen == "manage_blacklist":
            manage_blacklist()
        elif curr_screen == "select_song_setup":
            select_song_setup()
        elif curr_screen == "select_song":
            select_song()
        elif curr_screen == "playlists_setup":
            playlist_select_setup()
        elif curr_screen == "playlists":
            playlist_select()
        elif curr_screen == "bandle_setup":
            bandle_setup()
        elif curr_screen == "bandle" or curr_screen == "bandle_guessing" or curr_screen == "bandle_win" or curr_screen == "bandle_stare":
            bandle_screen()
            
        for i in range(len(warnings)-1, -1, -1):
            warnings[i].tick(screen)
            if warnings[i].death:
                warnings.pop(i)

        # flip() the display to put your work on screen
        scaled = pygame.transform.smoothscale(
            screen,
            window.get_size()
        )

        window.blit(scaled, (0, 0))
        pygame.display.flip()
        pygame.event.clear()  # clear event _b_queue
        counter += 1

        # managing fps
        clock.tick(con.TARGET_FPS)
        
    pygame.quit()



if __name__ == "__main__":
    main()