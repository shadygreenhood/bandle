

def main():
    import constants as con

    import audio_helper as audio_helper
    from modules import Button, Toggle, Textinput, Warning
    from multiprocessing import Process, freeze_support, Queue
    from console import main_console
    
    import pygame           # type: ignore
    import math
    import json

    from random import shuffle
    from pathlib import Path


    con.clear()
    con.logger.pretty_text("╭----------------------------------------------------------╮\n"\
                           "|      ╭=-.  ╭==╮  ╭╮ ╮  ╭-.   ╭    ╭=-       g  u  i      |\n"\
                           "|      ╞-:╯  ╞--╡  |╰╮|  |  |  |    ╞-        g  u  i      |\n"\
                           "|      ╰=-╯  ╰  ╯  ╰ ╰╯  ╰='   ╰-╯  ╰=-       g  u  i      |\n"\
                           "╰----------------------------------------------------------╯", "magenta bold")



    
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

    global curr_blacklist
    curr_blacklist = con.curr_blacklist

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

    def everything_black(is_black):
        if is_black:
            con.COLOR_PALETTE = {
                "background"            : (255-255, 255-255, 255-255),
                "face"                  : (255-217, 255-217, 255-217),
                "shadow"                : (255-127, 255-127, 255-127),
                "textinput unselected"  : (255-244, 255-244, 255-244),
                "textinput selected"    : (255-200, 255-200, 255-200),
                "list item unselected"  : (255-183, 255-183, 255-183),
                "list item selected"    : (255-145, 255-145, 255-145),
                "black"                 : (255-0  , 255-0,   255-0  ),
                "red accent"            : (195, 63 , 63 ),
                "guessing background"   : (255-242, 255-242, 255-242),
                "stems selected"        : (255-80 , 255-80 , 255-80 ),
                "rich magenta"          : (50 , 250, 50 ), # yes, magenta is green in dark mode, ik, makes perfect sense
                "rich blue"             : (50 , 60 , 200),
                "rich green"            : (200, 50 , 150), #
                "rich yellow"           : (238, 250, 15 ),
                "rich red"              : (200, 10 , 10 )
            }
        else:
            con.COLOR_PALETTE = {
                "background"            : (255, 255, 255),
                "face"                  : (217, 217, 217),
                "shadow"                : (127, 127, 127),
                "textinput unselected"  : (244, 244, 244),
                "textinput selected"    : (200, 200, 200),
                "list item unselected"  : (183, 183, 183),
                "list item selected"    : (145, 145, 145),
                "black"                 : (0  , 0,   0  ),
                "red accent"            : (195, 63 , 63 ),
                "guessing background"   : (242, 242, 242),
                "stems selected"        : (80 , 80 , 80 ),
                "rich magenta"          : (200, 50 , 150),
                "rich blue"             : (50 , 60 , 200),
                "rich green"            : (50 , 250, 50 ),
                "rich yellow"           : (238, 250, 15 ),
                "rich red"              : (200, 10 , 10 )
            }

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
                con.BLACKLISTS[curr_blacklist].append(_b_current_song)
                    
                
                if not silent:
                    warnings.append(Warning(f"song was {sanitize(_b_current_song)}", (40, con.HEIGHT-80, con.WIDTH-80), "info"))
                a = True
                while a:
                    _b_song_counter += 1
                    if _b_song_counter > len(_b_queue):
                        warnings.append(Warning(f"you finished the playlist!", (40, con.HEIGHT-80, con.WIDTH-80), "info"))
                        curr_screen = "playlists"
                        a = False
                    else:
                        _b_current_song = _b_queue[_b_song_counter - 1]
                        if Path(con.STEMS_FOLDER / _b_current_song).is_dir():
                            print("load anim in")

                            player.load(_b_current_song)
                            player.play(_b_step)
                            player.seek(player.audio_len/5)
                            player.toggle()
                            print("load anim out")
                                    
                            a = False
                        else:
                            warnings.append(Warning(f"couldnt find song folder", (40, con.HEIGHT-80, con.WIDTH-80), "warning"))
                            a = False

    def setup():
        
        # GUI SPECIFIC CONSTANTS
        global SHADOW_OFFSET
        SHADOW_OFFSET = 10

        # GUI specific vars
        global loading_anim_slider
        loading_anim_slider = 0
        global go_back_button
        go_back_button = Button(19, 23, 101, 48, "red accent", "Back", radius=15)
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
        global _mm_dark_mode_toggle

        global _mm_ANIM_SPEED
        _mm_ANIM_SPEED = 1/5



        if submenu == "setup":
            # prep for main menu + settings screen

            # sprites (mostly x=0 cuz its overwritten anyways)
            _mm_settings_button             = Button(0, 41 , 69, 50, "background", "", radius=20)
            _mm_search_button               = Button(0, 360, 329, 115,  "face", "Search", radius=20)
            _mm_library_button              = Button(0, 530 , 329, 115, "face", "Library", radius=20)
            _mm_manage_blacklist_button     = Button(0, 508, 229, 82,  "face", "Select\nblacklist", radius=20)
            _mm_open_console_button         = Button(0, 782, 229, 82,  "face", "Open\nConsole", radius=20)

            _mm_CHEAT_MODE_toggle =         Toggle(0, 262)
            _mm_global_suggestions_toggle = Toggle(0, 262+70, default=True)
            _mm_dark_mode_toggle =          Toggle(0, 262+140, default=True)

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
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 330))
            screen.blit(text_surface, text_rect)
            text_surface = con.basic_font.render("Suggestions", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 350))
            screen.blit(text_surface, text_rect)
            #Toggle text (Dark Mode)
            text_surface = con.basic_font.render("Dark Mode", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(-180 + con.WIDTH*_mm_x_spring_slider, 420))
            screen.blit(text_surface, text_rect)



            _mm_search_button.x           = 85    + con.WIDTH*_mm_x_spring_slider
            _mm_library_button.x          = 85    + con.WIDTH*_mm_x_spring_slider
            _mm_manage_blacklist_button.x = -448  + con.WIDTH*_mm_x_spring_slider
            _mm_open_console_button.x     = -448  + con.WIDTH*_mm_x_spring_slider

            _mm_CHEAT_MODE_toggle.x       = -448  + con.WIDTH*_mm_x_spring_slider
            _mm_global_suggestions_toggle.x = -448  + con.WIDTH*_mm_x_spring_slider
            _mm_dark_mode_toggle.x          = -448  + con.WIDTH*_mm_x_spring_slider

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

            _mm_dark_mode_toggle.draw(screen, events)
            if con.DARK_MODE != _mm_dark_mode_toggle.state:
                con.DARK_MODE = _mm_dark_mode_toggle.state
                everything_black(con.DARK_MODE)

            if _mm_library_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_library"
            if _mm_manage_blacklist_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_blacklists"
            if _mm_open_console_button.is_clicked(events):
                loading_anim_slider = 0
                submenu = "loading_terminal"  # need to add console
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
            

        if submenu in ["loading_library", "loading_blacklists", "loading_search", "loading_terminal"]:
            loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
            pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
            text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
            screen.blit(text_surface, text_rect)


            if abs((1-loading_anim_slider) * 100) < 1:
                if submenu == "loading_search":
                    submenu = "setup"
                    curr_screen = "select_song_setup"
                if submenu == "loading_terminal":
                    submenu = "setup"
                    curr_screen = "terminal_setup"
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
            
            
            _mb_close_button  = Button(388, 232, 50, 50, "list item unselected", "ok", 15)
            _mb_modify_button = Button(85, 790, 204, 52, "list item unselected", "Modify", 15)
            _mb_add_button    = Button(300, 790, 52, 52, "list item unselected", "+", 15)
            _mb_delete_button = Button(363, 790, 52, 52, "list item unselected", "d", 15)

            
            _mb_blacklist_buttons = []
            for i in range(len(con.BLACKLISTS_NAMES)):
                _mb_blacklist_buttons.append(Button(71, 536 + i*61, 358, 51, "list item unselected", con.BLACKLISTS_NAMES[i], 15))

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
                _mb_name_edit.text = con.BLACKLISTS_NAMES[curr_blacklist]
            else:
                for event in  events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # editing blacklist name
                        if not _mb_name_edit.text in con.BLACKLISTS_NAMES and _mb_name_edit.text != "":
                            con.BLACKLISTS_NAMES[curr_blacklist] = _mb_name_edit.text
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
                    if not "new_blacklist_" + str(i) in con.BLACKLISTS_NAMES:
                        break
                    i += 1
                n = f"new_blacklist_{i}"
                lines.append(n + "=")
                b = "\n".join(lines)
                with open(con.BLACKLISTS_DIR, "w") as f:
                    f.write(b)

                _mb_blacklist_buttons.append(Button(71, 536 + len(con.BLACKLISTS_NAMES)*61, con.WIDTH-140, 60, "list item unselected", n, 15))
                con.BLACKLISTS_NAMES.append(n)
                con.BLACKLISTS.append([])

            if _mb_delete_button.is_clicked(events):
                if not len(con.BLACKLISTS) < 2:

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
                    con.BLACKLISTS_NAMES.pop(curr_blacklist)
                    con.BLACKLISTS.pop(curr_blacklist)
                    if curr_blacklist > len(con.BLACKLISTS_NAMES)-1:
                        curr_blacklist -= 1 


    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if submenu == "loading_manage_blacklists":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "manage_blacklists"
                    loading_anim_slider = 0


            if submenu in ["loading_main_menu"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)


                if abs((1-loading_anim_slider) * 100) < 1:
                    if submenu == "loading_main_menu":
                        loading_anim_slider = 0
                        submenu = "loading_main_menu"
                        curr_screen = "main_menu"


    def terminal_setup():
        global submenu
        global curr_screen
        submenu = "setup"
        curr_screen = "terminal"

    def terminal():
        global curr_screen
        global submenu
        global go_back_button
        global loading_anim_slider
        
        global _t_p
        global _t_q_in
        global _t_q_out
        global _t_inputs
        global _t_logs
        global _t_textinput
        global _t_scrollpos
        global _t_scrollvel

        global _t_add_logs

        if submenu == "setup":
            
            _t_textinput = Textinput(20, con.HEIGHT - 50, con.WIDTH-20, 50, -1, con.COLOR_PALETTE["textinput unselected"])
            

            def _t_add_logs(str, style):
                global _t_logs

                lines = str.split("\n")

                for i in lines:
                    _t_logs.append([style, i])
                    # if new messages were progress bar updates, squish them
                    if len(_t_logs) > 0:
                        if _t_logs[-1][1][:14] == "[PROGRESS BAR]" and _t_logs[-2][1][:14] == "[PROGRESS BAR]":
                            _t_logs.pop(-2)
            _t_logs = []
            _t_inputs = []
            _t_scrollpos = 0
            _t_scrollvel = 0
            

            _t_q_in = Queue()
            _t_q_out = Queue()
            _t_p = Process(target=main_console, args=(_t_q_out, _t_q_in,))
            _t_p.start()

            loading_anim_slider = 0
            submenu = "loading_main"

            


        if submenu in ["main", "loading_main", "out_loading_main_menu", "loading_bandle"]:

            _t_textinput.focused = True
            if not _t_q_out.empty():
                message = _t_q_out.get()
                if message[0][0] == "input":
                    _t_inputs.append(message[0][1])
                    _t_add_logs(message[0][1], "black")
                else:
                    if message[0][0] == "debug":
                        _t_add_logs("[DEBUG]: "+message[0][1], "blue")
                    if message[0][0] == "warning":
                        _t_add_logs("[WARNING]: "+message[0][1], "yellow")
                    if message[0][0] == "error":
                        _t_add_logs("[ERROR]: "+message[0][1], "red")
                    if message[0][0] == "pretty":
                        _t_add_logs(message[0][1], message[0][2])


            _t_textinput.draw(screen, events)
            pygame.draw.rect(screen, con.COLOR_PALETTE["textinput selected"], pygame.Rect(0, con.HEIGHT-50, 20, 50))
            
            max_lines = 28
            for event in  events:
                if len(_t_inputs) > 0:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        _t_scrollpos = 0
                        _t_q_in.put(_t_textinput.text)
                        _t_add_logs(_t_textinput.text, "black")
                        _t_inputs.pop(0)
                        _t_textinput.text = ""

            indent = 1

            _t_scrollvel = (_t_scrollvel + (mouse_scroll)/17)/2
            _t_scrollpos = (_t_scrollpos + _t_scrollvel*10)
            if _t_scrollpos > len(_t_logs)-max_lines:
                _t_scrollpos = len(_t_logs)-max_lines
            if _t_scrollpos < 0:
                _t_scrollpos = 0
            for i in range(len(_t_logs) if len(_t_logs) < max_lines else max_lines):
                
                text = _t_logs[-1-i][1]
                
                
                
                if i == 0 and text == ">":
                    text_surface = con.basic_font.render(text, True, con.COLOR_PALETTE["black"])
                    screen.blit(text_surface, (0, con.HEIGHT - 50))
                    indent = 0
                else:

                    

                    ofs_idx = i+round(_t_scrollpos)
                    text = _t_logs[-1-ofs_idx][1]
                    

                    if text[:14] == "[PROGRESS BAR]":
                        text = text[14:]
                
                    # need to interpret [those] kinds of [/colors]
                    # if "[blue]" in text:
                    #     fragments = text.replace("[/blue]", "[blue]").split("[blue]")
                    #     print(fragments)
                        

                    line_color = con.COLOR_PALETTE["black"]
                    accidental_color = "none"

                    if "magenta" in _t_logs[-1-ofs_idx][0]:
                        # con.COLOR_PALETTE["rich magenta"]
                        line_color = con.COLOR_PALETTE["rich magenta"]
                    elif "red" in _t_logs[-1-ofs_idx][0]:
                        line_color = con.COLOR_PALETTE["rich red"]
                    elif "blue" in _t_logs[-1-ofs_idx][0]:
                        line_color = con.COLOR_PALETTE["rich blue"]
                    elif "yellow" in _t_logs[-1-ofs_idx][0]:
                        line_color = con.COLOR_PALETTE["rich yellow"]
                    skip_counter = 0
                    skip_total_offset = 0
                    for letter in range(len(text)):


                        # interpret accidental colors (support for blue, cyan, black, green
                        four_ltr_colors = ["blue", "cyan"]
                        five_ltr_colors = ["black", "green"]
                        
                        if text[letter] == "[":
                            
                            if text[letter+1] == "/":
                                slash = True
                            else:
                                slash = False

                            # if its one of the four lettered colours...
                            if text[letter+1+(1 if slash else 0): letter + 5 + (1 if slash else 0)] in four_ltr_colors:
                                color_len = 4
                            # if its one of the five lettered colours...
                            elif text[letter+1+(1 if slash else 0): letter + 6 + (1 if slash else 0)] in five_ltr_colors:
                                color_len = 5
                                
                            if slash == True:
                                accidental_color = "none"
                                skip_counter = color_len + 3
                                skip_total_offset += color_len + 3
                            else:
                                if color_len == 4:
                                    for j in four_ltr_colors:
                                        if text[letter+1: letter + 5] == j:
                                            accidental_color = con.COLOR_PALETTE["rich "+j]
                                elif color_len == 5:
                                    for j in five_ltr_colors:
                                        if text[letter+1: letter + 6] == j:
                                            accidental_color = con.COLOR_PALETTE["rich "+j]
                                skip_counter = color_len + 2
                                skip_total_offset += color_len + 2

                        if skip_counter == 0:    
                            text_surface = con.terminal_font.render(text[letter], True, line_color if accidental_color == "none" else accidental_color)
                            screen.blit(text_surface, (5+(letter - skip_total_offset)*9, con.HEIGHT - (50 + (i+indent)*30)))
                        skip_counter -= 1 if skip_counter > 0 else 0

            # header
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))
            text_surface = con.small_font.render("Terminal", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (con.WIDTH/2 + 55 - text_surface.get_width()/2,20 + go_back_button.h/2 - 18))
            go_back_button.draw(screen)
            if go_back_button.is_clicked(events) == 1:
                # killing console process
                _t_p.terminate()
                # reevaluating song accessibility
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

                submenu = "out_loading_main_menu"

            
    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if submenu == "loading_main":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "main"
                    loading_anim_slider = 0

            if submenu in ["out_loading_main_menu"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*3/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if submenu == "out_loading_main_menu":
                    if abs((1-loading_anim_slider) * 100) < 1:
                        submenu = "loading_main_menu"
                        curr_screen = "main_menu"
                        loading_anim_slider = 0


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

            _ss_library_button =            Button(0, con.HEIGHT-100, con.WIDTH/2, 100, "list item unselected", "")
            _ss_global_search_button =      Button(con.WIDTH/2, con.HEIGHT-100, con.WIDTH/2, 100, "face", "")
            _ss_select_song_button =        Button(20,700, con.WIDTH, 35, "face", "", radius=10)
            _ss_textinput =                 Textinput(50, 160, con.WIDTH - 100, 50, 5, "textinput unselected")

            _ss_categories = []
            for i in range(len(con.CATEGORIES)):
                _ss_categories.append(Button(81 + (i%2)*(178), 389 + math.floor(i/2)*87, 160, 70, "list item selected", con.CATEGORIES[i], radius=15))

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
            o = 350
            _ss_scrollvel = (_ss_scrollvel + mouse_scroll*5)/2
            _ss_scrollpos = _ss_scrollpos + _ss_scrollvel*10
            if _ss_scrollpos < len(selection) * -38 + 106+725-o:
                _ss_scrollpos = len(selection) * -38 + 106+725-o
            if _ss_scrollpos > 0:
                _ss_scrollpos = 0

            # placing a button under the cursor if hovering on the options
            if mouse_y > o + _ss_scrollpos and mouse_y < con.HEIGHT-106 and mouse_y > 200:
                _ss_selected = math.floor((mouse_y-o-_ss_scrollpos)/38)
                _ss_select_song_button.y = math.floor((mouse_y-o-_ss_scrollpos)/38) * 38 + o + _ss_scrollpos
                if _ss_selected < len(selection):
                    _ss_select_song_button.draw(screen)
                    if _ss_select_song_button.is_clicked(events):
                        if all_songs_sanitized_availability[all_songs_sorted.index(selection[_ss_selected])] == False:
                            warnings.append( Warning("this song isnt available", (40, con.HEIGHT-80, con.WIDTH-80), level="warning"))
                        else:
                            _b_current_song = all_songs[all_songs.index(selection[_ss_selected])]
                            submenu = "loading_bandle"

            # render options text
            for i in range(len(selection)):
                if o + _ss_scrollpos + i*38 > 0 and o + _ss_scrollpos + i*38 < con.HEIGHT:
                    text_surface = con.small_font.render(sanitize(selection[i]), True, con.COLOR_PALETTE["black"])
                    if all_songs_sanitized_availability[all_songs_sorted.index(selection[i])] == False:
                        text_surface = con.small_font.render(sanitize(selection[i]), True, con.COLOR_PALETTE["list item unselected"])
                    screen.blit(text_surface, (40,o + _ss_scrollpos + i*38))


            # Songs header
            text_surface = con.title_font.render("Songs", True, con.COLOR_PALETTE["black"])
            screen.blit(text_surface, (81,230 + _ss_scrollpos))
            
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
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "search"
                    loading_anim_slider = 0


            if submenu in ["loading_main_menu", "loading_bandle"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
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
            
            _ps_start_button = Button(135, 774, 229, 92, "face", "Start", radius=20, click_counter=20)


            for i in range(len(list(playlists_json_dir_contents.keys()))):
                _ps_playlist_buttons.append(Button(86, 247 + i*62, 328, 52, "list item unselected", playlists_json_dir_contents[list(playlists_json_dir_contents.keys())[i]]["name"], radius=15, info=list(playlists_json_dir_contents.keys())[i]))
            
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
                    _ps_playlist_buttons[i].color = "list item selected"
                else:
                    _ps_playlist_buttons[i].color = "list item unselected"
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
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "main"
                    loading_anim_slider = 0

            if submenu in ["out_loading_main_menu", "loading_bandle"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
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
        global _b_popup_guess_offset
        global _b_popup_guess_vel
        global _b_popup_win_offset
        global _b_popup_win_vel

        global _b_skip_button
        global _b_play_button
        global _b_guess_button
        global _b_skip_ahead
        global _b_skip_ahead_img
        global _b_rewind
        global _b_rewind_img
        global _b_play_img
        global _b_pause_img
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
        _b_popup_guess_offset = 0
        _b_popup_guess_vel = 0
        _b_popup_win_offset = 0
        _b_popup_win_vel = 0

        # setting buttons
        _b_play_button  = Button(213 , 750, 75 , 65 , "list item selected", ""      , radius=15, click_counter=20)
        _b_skip_button  = Button(388, 741, 95 , 83 , "list item selected", "Skip"      , radius=15, click_counter=20)
        _b_guess_button = Button(16 , 741, 95 , 83 , "list item selected", "Guess", radius=15, click_counter=20)

        _b_rewind =     Button(con.WIDTH/2 - 45 -90  , con.HEIGHT -210, 90 , 85 , "background", ""      , radius=20, click_counter=20)
        _b_skip_ahead = Button(con.WIDTH/2 + 45      , con.HEIGHT -210, 90 , 85 , "background", ""      , radius=20, click_counter=20)
        
        _b_skip_ahead_img = pygame.image.load(con.ASSETS_DIR / "skip_ahead.png").convert_alpha()
        _b_skip_ahead_img = pygame.transform.smoothscale(_b_skip_ahead_img, (60, 60))

        _b_rewind_img = pygame.image.load(con.ASSETS_DIR / "rewind.png").convert_alpha()
        _b_rewind_img = pygame.transform.smoothscale(_b_rewind_img, (60, 60))

        _b_play_img = pygame.image.load(con.ASSETS_DIR / "play_head.png").convert_alpha()
        _b_play_img = pygame.transform.smoothscale(_b_play_img, (32, 36))

        _b_pause_img = pygame.image.load(con.ASSETS_DIR / "pause_head.png").convert_alpha()
        _b_pause_img = pygame.transform.smoothscale(_b_pause_img, (32, 36))

        textinput = Textinput(60, con.HEIGHT, 380, 49, 10, con.COLOR_PALETTE["textinput unselected"])



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
                if _b_queue[i] in con.BLACKLISTS[curr_blacklist]:
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
        global _b_popup_guess_offset
        global _b_popup_guess_vel
        global _b_popup_win_offset
        global _b_popup_win_vel
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
        global _b_play_img
        global _b_pause_img
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
            player.update_pointer()
            progression = player.pointer * 1000 / player.audio_len if player.audio_len != 0 else 0

        # ╭----------------------------------------╮
        # |      ╭  ╮ ╭=-  ╭==╮ ╭-.  ╭=- ╭==╮      |
        # |      ╞--╡ ╞-   ╞--╡ |  | ╞-  ╞=:╯      |
        # |      ╰  ╯ ╰=-  ╰  ╯ ╰='  ╰=- ╰  ╰      |
        # ╰----------------------------------------╯
            # title text
            bandle_title = con.title_font.render("Bandle", True, con.COLOR_PALETTE["black"])
            screen.blit(bandle_title, (con.WIDTH/2 - bandle_title.get_width()/2,120))
            
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
                    
                    b = Button(71, 246 + i*74, 361, 60, "black", f"{con.STEMS[i]}", 15)
                    
                    b.draw(screen)
                    if b.is_clicked(events):
                        _b_step = i
                        skip(True, simple_update=True)
                    # pygame.draw.rect(screen, (200, 200, 200) if i < _b_step else (150, 150, 150), pygame.Rect(50, 250 + i*80, con.WIDTH - 100, 60), border_radius=15)
                    # stem_text = con.basic_font.render(f"{con.STEMS[i]}", True, con.COLOR_PALETTE["black"])
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
                        player.stop_all()
                        _b_loading_status = "out_loading_song"
                    else:
                        # here, bandle_stare is the only mode that should both be silent (no warnings) and simple_update (no going back to the start of the song)
                        skip(True if submenu == "bandle_stare" else False, True if submenu == "bandle_stare" else False)
                    if _b_step == len(con.STEMS):
                        _b_skip_button.text = "Next\nSong"
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
            _b_play_button.draw(screen)
            if  player.status != "Playing":
                screen.blit(_b_play_img, (237 ,  765))
            else:
                screen.blit(_b_pause_img, (235 ,  765))
            
            if submenu != "bandle_guessing":
                if _b_play_button.is_clicked(events) == 1:
                    player.curr_step = _b_step    
                    player.toggle()

        # ╭----------------------------------------------------------------------------╮
        # |      ╭==╮ ╭  ╮ ╭=- ╭==╮ ╭==╮  .  ╭╮ ╮ ╭==╮   ╭==╮ ╭==╮ ╭==╮ ╭  ╮ ╭==╮      |
        # |      |  ╮ |  | ╞-  ╰--╮ ╰--╮  |  |╰╮| |  ╮   ╞==╯ |  | ╞==╯ |  | ╞==╯      |
        # |      ╰==╯ ╰==╯ ╰=- ╰==╯ ╰==╯  ╰  ╰ ╰╯ ╰==╯   ╰    ╰==╯ ╰    ╰==╯ ╰         |
        # ╰----------------------------------------------------------------------------╯
            # bandle guessing screen popup
            if submenu == "bandle_guessing":
                
                _b_popup_guess_vel += (1 - _b_popup_guess_offset) * 0.05 - (_b_popup_guess_vel*0.3)
                
                _b_popup_guess_offset += _b_popup_guess_vel

                #popup
                pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, con.HEIGHT-(con.HEIGHT-460)*_b_popup_guess_offset, con.WIDTH, 600), border_radius=20)
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(5, con.HEIGHT-(con.HEIGHT-465)*_b_popup_guess_offset, con.WIDTH-10, 600), border_radius=15)
                text_surf = con.basic_font.render("Have an idea?", True, con.COLOR_PALETTE["black"])
                screen.blit(text_surf, (150, con.HEIGHT - (con.HEIGHT - 491)*_b_popup_guess_offset))

                textinput.y = con.HEIGHT - (con.HEIGHT-543)*_b_popup_guess_offset
                pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(55, con.HEIGHT-(con.HEIGHT-538)*_b_popup_guess_offset, 390, 59), border_radius=15)
                textinput.draw(screen, events)
                

                limit = 8
                text = textinput.text
                suggestions = []
                actual_suggestions = []
                
                if con.GLOBAL_SUGGESTIONS or _b_single_song_bool:
                    options = all_songs_sanitized
                else:
                    options = [playlists_json_dir_contents[selected_playlist]["data"][i]["name"][:-9] for i in range(len(playlists_json_dir_contents[selected_playlist]["data"]))]

                for i in range(len(options)):
                    if text.lower() in options[i].lower():
                        if options[i] not in suggestions:
                            suggestions.append(options[i])
                            actual_suggestions.append(all_songs[i])
                    elif text.lower() in con.SONGS_JSON_DIR_contents[all_songs[i]]["baked_artists"]:
                        if options[i] not in suggestions:
                            suggestions.append(options[i])
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
                    pygame.draw.rect(screen, con.COLOR_PALETTE["list item selected"], pygame.Rect(20, con.HEIGHT -  (con.HEIGHT - 617)*_b_popup_guess_offset + (selected-offset)*40, con.WIDTH-20, 30), border_radius=5)

                for i in suggestions:
                    suggestion_surf = con.basic_font.render(i, True, con.COLOR_PALETTE["black"])
                    screen.blit(suggestion_surf, (70, con.HEIGHT + suggestions.index(i)*40 -  (con.HEIGHT - 608)*_b_popup_guess_offset))

                _b_bandle_guessing_counter += 1/30
                if _b_bandle_guessing_counter > 1:
                    _b_bandle_guessing_counter = 1

            else:
                _b_popup_guess_vel += (0 - _b_popup_guess_offset) * 0.05 - (_b_popup_guess_vel*0.3)
                
                _b_popup_guess_offset += _b_popup_guess_vel

                #popup
                pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, con.HEIGHT-(con.HEIGHT-460)*_b_popup_guess_offset, con.WIDTH, 600), border_radius=20)
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(5, con.HEIGHT-(con.HEIGHT-465)*_b_popup_guess_offset, con.WIDTH-10, 600), border_radius=15)
                
                pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(55, con.HEIGHT-(con.HEIGHT-538)*_b_popup_guess_offset, 390, 59), border_radius=15)
                pygame.draw.rect(screen, con.COLOR_PALETTE["textinput unselected"], pygame.Rect(60, con.HEIGHT-(con.HEIGHT-543)*_b_popup_guess_offset, 380, 49), border_radius=15)
                text_surf = con.basic_font.render("Have an idea?", True, con.COLOR_PALETTE["black"])
                screen.blit(text_surf, (150, con.HEIGHT - (con.HEIGHT - 491)*_b_popup_guess_offset))

                limit = 9
                text = textinput.text
                suggestions = []
                actual_suggestions = []
                for i in range(len(all_songs_sanitized)):
                    if text.lower() in all_songs_sanitized[i].lower():
                        if all_songs_sanitized[i] not in suggestions:
                            suggestions.append(all_songs_sanitized[i])
                            actual_suggestions.append(all_songs[i])
                    elif text.lower() in con.SONGS_JSON_DIR_contents[all_songs[i]]["baked_artists"]:
                        if all_songs_sanitized[i] not in suggestions:
                            suggestions.append(all_songs_sanitized[i])
                            actual_suggestions.append(all_songs[i])

                suggestions = suggestions[offset:offset + limit]
                

                if selected != -1:
                    pygame.draw.rect(screen, con.COLOR_PALETTE["list item selected"], pygame.Rect(20, con.HEIGHT -  (con.HEIGHT - 617)*_b_popup_guess_offset + (selected-offset)*40, con.WIDTH-20, 30), border_radius=5)

                for i in suggestions:
                    suggestion_surf = con.basic_font.render(i, True, con.COLOR_PALETTE["black"])
                    screen.blit(suggestion_surf, (70, con.HEIGHT + suggestions.index(i)*40 -  (con.HEIGHT - 608)*_b_popup_guess_offset))

                _b_bandle_guessing_counter += 1/30
                if _b_bandle_guessing_counter > 1:
                    _b_bandle_guessing_counter = 1

        # ╭-----------------------------------------------------------------------╮
        # |      ╭   ╮  .  ╭=-╮ ╭=╮ ╭==╮ ╭==╮ ╮ ╭    ╭==╮ ╭==╮ ╭==╮ ╭  ╮ ╭==╮     |
        # |      '   '  |  |     |  |  | ╞=:╯ ╰╮╯    ╞==╯ |  | ╞==╯ |  | ╞==╯     |
        # |       ╰=╯   ╰  ╰=-╯  ╰  ╰==╯ ╰  ╰  ╯     ╰    ╰==╯ ╰    ╰==╯ ╰        |
        # ╰-----------------------------------------------------------------------╯
            if submenu == "bandle_win":
                
                _b_popup_win_vel += (1 - _b_popup_win_offset) * 0.05 - (_b_popup_win_vel*0.3)
                
                _b_popup_win_offset += _b_popup_win_vel


                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0, -con.HEIGHT + (con.HEIGHT - 43)*_b_popup_win_offset, con.WIDTH, con.HEIGHT), border_radius=20)
                win_text = con.title_font.render("YOU WON", True, con.COLOR_PALETTE["black"])
                screen.blit(win_text, (100, 120*_b_popup_win_offset))

                if not _b_single_song_bool:
                    pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(85 + SHADOW_OFFSET, -200+(200+360)*_b_popup_win_offset + SHADOW_OFFSET, 329, 115), border_radius=20)
                    butt = Button(85, -200+(200+360)*_b_popup_win_offset, 329, 115, "face", "go back and\nadmire", 20)
                    butt.draw(screen)
                    if butt.is_clicked(events):
                        submenu = "bandle_stare"
                    pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(85 + SHADOW_OFFSET, -200+(200+530)*_b_popup_win_offset + SHADOW_OFFSET, 329, 115), border_radius=20)                    
                    next = Button(85, -200+(200+530)*_b_popup_win_offset, 329, 115, "face", "go next", 20)
                    next.draw(screen)
                    if next.is_clicked(events):
                        skip(True, True)
                        submenu = "bandle"
                else:
                    pygame.draw.rect(screen, con.COLOR_PALETTE["shadow"], pygame.Rect(85 + SHADOW_OFFSET, -200+(200+360)*_b_popup_win_offset + SHADOW_OFFSET, 329, 115), border_radius=20)
                    next = Button(85, -200+(200+360)*_b_popup_win_offset, 329, 115, "face", "Return to selection", 20)
                    next.draw(screen)
                    if next.is_clicked(events):
                        player.stop_all()
                        _b_loading_status = "out_loading_song"

                    
                
            else:
                _b_popup_win_vel += (0 - _b_popup_win_offset) * 0.05 - (_b_popup_win_vel*0.3)
                
                _b_popup_win_offset += _b_popup_win_vel
        
        
        # ╭----------------------------------------╮
        # |      ╭  ╮ ╭=-  ╭==╮ ╭-.  ╭=- ╭==╮      |
        # |      ╞--╡ ╞-   ╞--╡ |  | ╞-  ╞=:╯      |
        # |      ╰  ╯ ╰=-  ╰  ╯ ╰='  ╰=- ╰  ╰      |
        # ╰----------------------------------------╯
            pygame.draw.rect(screen, con.COLOR_PALETTE["face"], pygame.Rect(0, -50, con.WIDTH, 145))

            
            
            # selected playlist text (cool little script)
            if not curr_screen == "bandle_win":
                if not _b_single_song_bool:
                    selected_playlist_text = f"Selected playlist: {playlists_json_dir_contents[selected_playlist]['name']}"
                else:
                    selected_playlist_text = f"testing single song"
            else:
                selected_playlist_text = f"got the duuuub"
            words = selected_playlist_text.split(" ")
            wordlines = []

            for i in range(len(words)):
                for j in range(len(words)):
                    if sum(len(words[i]) for i in range(len(words) - j)) < 25 or j == len(words) - 1:

                        selected_playlist_text = "".join((words[i] + " ") for i in (range(len(words) - j)))
                        selected_playlist_text = selected_playlist_text[:-1]
                        wordlines.append(selected_playlist_text)

                        for i in range(len(words[:len(words) - j])):
                            words.pop(0)
                        break
                if words == []:
                    break
            
            for i in range(len(wordlines)):
                selected_playlist_text = con.small_font.render(wordlines[i], True, con.COLOR_PALETTE["black"])
                screen.blit(selected_playlist_text, (con.WIDTH/2 + 55 - selected_playlist_text.get_width()/2,20 + go_back_button.h/2 - 18 - (len(wordlines)-1)*30/2 + i*30))

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


    # ╭---------------------------------------------------------------------------------------------╮
    # |      ╭    ╭==╮  ╭==╮  ╭-.   .  ╭╮ ╮  ╭==╮       ╭==╮  ╭=-╮  ╭==╮  ╭=-  ╭=-  ╭╮ ╮  ╭==╮      |
    # |      |    |  |  ╞--╡  |  |  |  |╰╮|  |  ╮       ╰--╮  |     ╞=:╯  ╞-   ╞-   |╰╮|  ╰--╮      |
    # |      ╰-╯  ╰==╯  ╰  ╯  ╰='   ╯  ╰ ╰╯  ╰==╯       ╰==╯  ╰=-╯  ╰  ╰  ╰=-  ╰=-  ╰ ╰╯  ╰==╯      |
    # ╰---------------------------------------------------------------------------------------------╯
            if _b_loading_status == "loading_in":
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(0 -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
                text_rect = text_surface.get_rect(center=(con.WIDTH*1/2 - loading_anim_slider*con.WIDTH, con.HEIGHT/2))
                screen.blit(text_surface, text_rect)

                if abs((1-loading_anim_slider) * 100) < 1:
                    submenu = "bandle"
                    loading_anim_slider = 0
                    _b_loading_status = "nope"

            if _b_loading_status in ["out_loading_playlist", "out_loading_song"]:
                loading_anim_slider += (1 - loading_anim_slider)*_mm_ANIM_SPEED
                pygame.draw.rect(screen, con.COLOR_PALETTE["guessing background"], pygame.Rect(con.WIDTH -loading_anim_slider*con.WIDTH,0, con.WIDTH, con.HEIGHT))
                text_surface = con.title_font.render("Loading", True, con.COLOR_PALETTE["black"])
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
        elif curr_screen == "terminal_setup":
            terminal_setup()
        elif curr_screen == "terminal":
            terminal()
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
        counter += 1

        # managing fps
        clock.tick(con.TARGET_FPS)

    pygame.quit()



if __name__ == "__main__":
    main()