import pygame
import os
import csv
import ast
import sys
import vlc
from time import sleep 
import random
import math
from pathlib import Path



# constants
if "/" in str(Path(__file__)):
    PROJECT_DIR =  "/".join(str(Path(__file__).resolve().parent).split("/")[:-1])
elif "\\" in str(Path(__file__)):
    PROJECT_DIR =  "\\".join(str(Path(__file__).resolve().parent).split("\\")[:-1])
else:
    raise Exception(f"failed to resolve current project directory with cwd={str(Path(__file__))}")
SCRIPT_DIR = "bandle"
STEMS_FOLDER = PROJECT_DIR+"/separated/htdemucs_6s"
JAPANESE_FONT_DIR = PROJECT_DIR+"/Noto_Sans_JP/static/NotoSansJP-Medium.ttf"
PLAYLIST_CSV = PROJECT_DIR+"/"+SCRIPT_DIR+"/playlist_CSV.txt"
DEBUG = False
WIDTH = 500
HEIGHT = 950
CF_SCALE = 1
CHEAT_MODE = False
STEMS = ["drums", "bass", "guitar", "piano", "vocals", "other"]
SANITIZED_EXEPTIONS = {
    "Undertale_-_Spider_Dance_-_Shirobon_Remix": "Spider Dance",
}
CHARS = "AZERTYUIOPQSDFGHJKLMWXCVBNazertyuiopqsdfghjklmwxcvbn ,?;.:/!1234567890éè_&"
CF_DEBUG_VLC = False


# vars
playlist_to_names = {}
name_to_playlists = {}
playlist_to_songs = {}
playlists = []
friendly_names = []
all_songs = []
vlc_instance = vlc.Instance()
players = []
volume = 50
blacklists = "None"
blacklist_names = []
curr_blacklist = -1

# help function for debugging
def help(error=""):
    print(f"There was an error while parsing the arguments: {sys.argv[1:]}:")
    print(str(error))
    print("\n" \
    "this script is the GUI for the shadygreenhood bandle project\n" \
    "\n" \
    "Usage: mixer2.py [option]\n" \
    "\n" \
    "\n" \
    "Options:\n" \
    "--scale        final render scale of the window (0 to 1)\n" \
    "\n" \
    "\n")
    raise Exception(str(error))

# read Blacklists.txt
with open(f"{PROJECT_DIR}/{SCRIPT_DIR}/Blacklists.txt", "r") as f:
    txt = f.read().splitlines()
    blacklists = []
    for i in txt:
        try:
            blacklists.append([j for j in i.split("=")[1].split(" ")])
            blacklist_names.append(i.split("=")[0])
        except:
            help(f"failed to extract contents of {i} in Blacklists.txt")
        if blacklists[-1][-1] == "":
            blacklists[-1].pop(-1)
if blacklists == []:
    print("no blacklists found in Blacklist.txt, creating a new one")
    with open(f"{PROJECT_DIR}/{SCRIPT_DIR}/Blacklists.txt", "w") as f:
        f.write("GENERATED_BLACKLIST=")
    blacklists = [[""]]
    blacklist_names = ["GENERATED_BLACKLIST"]



# read config
with open(f"{PROJECT_DIR}/config.txt", "r") as f:
    txt = f.read().splitlines()
    for i in txt:
        if "SCALE" in i:
            if len(i.split("=")) > 0:
                try:
                    CF_SCALE = float(i.split("=")[1])
                except:
                    help("failed to convert " + str(i.split("=")[1]) + "to a float" )
            else:
                help(f"no scale provided in {PROJECT_DIR}/config.txt")
        if "DEBUG_VLC" in i:
            if len(i.split("=")) > 0:
                try:
                    CF_DEBUG_VLC = False if i.split("=")[1] == "False" else True if i.split("=")[1] == "True" else CF_DEBUG_VLC
                except:
                    help(f"failed to convert" + str(i.split("=")[1]) + "to a bool")
            else:
                help(f"no scale provided in {PROJECT_DIR}/config.txt")
        if "DEFAULT_BLACKLIST" in i:
            if len(i.split("=")) > 0:
                curr_blacklist = str(i.split("=")[1])
                if curr_blacklist in blacklist_names:
                    curr_blacklist = blacklist_names.index(curr_blacklist)
                else:
                    help("default blacklist is set to an unknown value")
            else:
                help(f"no blacklist provided after DEFAULT_BLACKLIST= in {PROJECT_DIR}/{SCRIPT_DIR}/Blacklists.txt")

if curr_blacklist == -1:
    print("no default blacklist found in config.txt defaulting to the first")
    curr_blacklist = 0

# deal with flags
args = sys.argv[1:]
for i in args:
    if i.startswith('--scale='):
        if len(i.split("=", 1)) > 0:
            CF_SCALE = float(i.split("=", 1)[1])
        else:
            help("no scale provided")
    else:
        raise help("argument not recognized")
    

# ╭----------------------------------------╮
# |      ╭----╮  ╭    ╮ ╭--,  ╭---╮ ╭----╮ |
# |      |    |  |    | |   \   |   |    | |
# |      |----|  |    | |   |   |   |    | |
# |      |    |  |    | |   /  _|_  |    | |
# |      ╰    ╯  ╰----╯ ╰--'  ╰---╯ ╰----╯ |
# ╰----------------------------------------╯

for i in range(len(STEMS)):
    player = vlc_instance.media_player_new()
    players.append(player)

def on_end(event):
    global vlc_on_end_sig
    vlc_on_end_sig = True
    
vlc_event_manager = players[0].event_manager()
vlc_on_end_sig = False
vlc_event_manager.event_attach(
    vlc.EventType.MediaPlayerEndReached,
    on_end
)

def load_song(stempath):
    for i in range(len(players)):
        players[i].stop()
        media = vlc_instance.media_new(stempath + f"/{STEMS[i]}.wav")
        players[i].set_media(media)
        players[i].play()
        while str(players[i].get_state()) not in ["State.Paused", "State.Playing"]:
            sleep(0.001)
        players[i].pause()
        set_position(0) 

def mute_all():
    for i in players:
        i.stop()

def set_position(pos):
    for i in range(len(players)):
        players[i].set_position(pos)

def debug_vlc():
    print("\n\n")
    for i in range(len(players)):
        
        info = [i]
        info.append(players[i].get_state())
        info.append(players[i].get_time())
        info.append(players[i].get_length())
        info.append(players[i].get_position())
        info.append(players[i].get_rate())
        info.append(players[i].audio_get_volume())
        info.append(players[i].is_playing())
        try:   
            info.append("yes" if i < step else "no")
        except:
            info.append("idk")
        strr = ""
        for j in range(len(info)):
            strr += ("|"+ str(info[j])[:10] + (10-len(str(info[j])[:10]))*" " +" |") if len(str(info[j])[:10])<10 else "|"+ str(info[j])[:10]+" |"
        print(strr)

def set_volume(step, volume=50):
    for i in range(len(players)):
        if i < step:
            players[i].audio_set_volume(volume)
        else:
            players[i].audio_set_volume(0)

def play_step():
    for i in range(len(players)):
        players[i].play()

def pause():
    for i in range(len(players)):
        players[i].pause()

def offset_players(offset):
    offset = players[0].get_time() + offset

    if offset >= players[0].get_length():
        offset = players[0].get_length()
    elif offset < 0:
        offset = 0
    
    for i in range(len(players)):
        players[i].set_time(offset)

def set_time(timestamp):
    for i in players:
        i.set_time(timestamp)






#fetch basic data from playlist csv
with open(PLAYLIST_CSV, newline='', encoding='utf-8') as fh:
    # some header stuff i dont fully understand
    reader = csv.reader(fh)
    headers = next(reader, [])
    headers = [h.strip() for h in headers]

    playlist_idx = 0
    friendly_name_idx = 1
    songs_idx = 2
    playlist = ""
    friendly_name = ""

    for row in reader:
        if len(row) > max(playlist_idx, songs_idx, friendly_name_idx):

            playlist = row[playlist_idx].strip()
            if playlist and playlist not in playlists:
                playlists.append(playlist)

            friendly_name = row[friendly_name_idx].strip()
            if friendly_name and friendly_name not in friendly_names:
                friendly_names.append(friendly_name)

            if playlist and friendly_name:
                if playlist not in playlist_to_names:
                    playlist_to_names[playlist] = friendly_name
                if friendly_name not in name_to_playlists:
                    name_to_playlists[friendly_name] = playlist

            playlist_songs = [s.replace(" ", "_") for s in ast.literal_eval(row[songs_idx].strip())]

            for i in playlist_songs:
                if i not in all_songs:
                    all_songs.append(i)

            if playlist and playlist_songs:
                if playlist not in playlist_to_songs:
                    playlist_to_songs[playlist] = playlist_songs


def sanitize(text):
    if text in SANITIZED_EXEPTIONS:
        sanitized = SANITIZED_EXEPTIONS[text]
        return sanitized
    
    sanitized = text.replace("_", " ")
    if "(" in sanitized:
        sanitized = sanitized.split("(")[0].strip()
    if "-" in sanitized:
        sanitized = sanitized.split("-")[0].strip()
    
    return sanitized

all_songs_sanitized = []

for i in all_songs:
    sanitized = sanitize(i)
    all_songs_sanitized.append(sanitized)

if DEBUG:
    print ("playlist_to_names")
    print (playlist_to_names)
    print ("playlist_to_songs")
    print (playlist_to_songs)
    print ("songs")
    print (all_songs)
    print ("playlists")
    print (playlists)
    print ("friendly_names")
    print (friendly_names)  


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


window = pygame.display.set_mode((WIDTH*CF_SCALE, HEIGHT*CF_SCALE)) 
screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

try:
    small_font = pygame.font.Font(JAPANESE_FONT_DIR, 25)
    basic_font = pygame.font.Font(JAPANESE_FONT_DIR, 30)
    title_font = pygame.font.Font(JAPANESE_FONT_DIR, 60)
except:
    small_font = pygame.font.SysFont('Comic Sans MS', 25)
    basic_font = pygame.font.SysFont('Comic Sans MS', 30)
    title_font = pygame.font.SysFont('Comic Sans MS', 80)




# ╭--------------------------------------------------------------------╮
# |      ╭----   ╭----╮ ╭-╮╭-╮ ╭----     ╭---╮  ╭╮   ╮ ╭---╮ ╭---╮     |
# |      |       |    | | ╰╯ | |           |    |╰╮  |   |     |       |
# |      |    ╮  |----| |    | |--         |    | ╰╮ |   |     |       |
# |      |    |  |    | |    | |          _|_   |  ╰╮|  _|_    |       |
# |      ╰----╯  ╰    ╯ ╰    ╯ ╰----     ╰---╯  ╰   ╰╯ ╰---╯   |       |
# ╰--------------------------------------------------------------------╯

def scale_mouse_pos(pos):
    return (pos[0]*(1/CF_SCALE),pos[1]*(1/CF_SCALE))


class Button:
    def __init__(self, x, y, w, h, color, text, radius=-1, click_counter=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.radius = radius
        self.rect = pygame.Rect(x, y, w, h)
        self.click_counter = click_counter


    def draw(self, surface, color=-1):

        if color == -1:
            display_color = self.color
        else:
            display_color = color

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, display_color, self.rect, border_radius=self.radius)

        text_surface = basic_font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.click_counter += 1
                    return self.click_counter
                self.click_counter = 0
                return 0
            self.click_counter = 0
            return 0
    ### TODO prevent it from incrementing clickcounter more than once per frame

class Toggle:
    def __init__(self, x, y, w, h, color_on, color_off, text_on, text_off, radius=-1, label=True):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color_on = color_on
        self.color_off = color_off
        self.text_on = text_on
        self.text_off = text_off
        self.radius = radius
        self.state = False
        self.offpos  = self.x + self.radius
        self.onpos = self.x + 100 - self.radius
        self.togl_head = pygame.Rect(self.onpos if self.state else self.offpos, self.y - self.h/4, 80, self.h)
        self.velocity = 0
        self.label = label
        

        opt1 = basic_font.render(self.text_on, True, (0, 0, 0))
        opt1 = opt1.get_width()
        opt2 = basic_font.render(self.text_off, True, (0, 0, 0))
        opt2 = opt2.get_width()

        self.biggest_text = max(opt2, opt1)
        self.centering_offset = -(self.radius-self.togl_head.width/2) - ((((self.togl_head.width/2 - self.radius + 120 + self.biggest_text) - (self.w)) / 2) if self.label else 0)
        self.togl_head = pygame.Rect(self.onpos if self.state else self.offpos, self.y - self.h/4, 80, self.h)
        self.offpos  = self.x + self.radius + self.centering_offset
        self.onpos = self.x + 100 - self.radius + self.centering_offset
    
    def draw(self, surface):

        rect = pygame.Rect(self.x + self.centering_offset, self.y, 100, self.h/2)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.togl_head.collidepoint(event.pos) or rect.collidepoint(event.pos):
                    self.state = not self.state

        dest = self.onpos if self.state else self.offpos
        offset = dest - self.togl_head.centerx 
        self.velocity += offset * 0.2 - self.velocity * 0.4
        if abs(offset) < 0.5 and self.velocity < 0.0008:
            self.velocity = 0
        self.togl_head.x += self.velocity
        
        pygame.draw.rect(surface, (90, 90, 90), rect, border_radius=self.radius)
        rect.inflate_ip(-10, -10)
        pygame.draw.rect(surface, (80, 80, 80), rect, border_radius=self.radius)

        color = self.color_on if self.state else self.color_off
        
        pygame.draw.rect(surface, (100, 100, 100), self.togl_head, border_radius=self.radius)
        self.togl_head.inflate_ip(-10, -10)
        pygame.draw.rect(surface, color, self.togl_head, border_radius=self.radius)
        self.togl_head.inflate_ip(10, 10)




        text_surface1 = basic_font.render(self.text_on if self.state else self.text_off, True, (0, 0, 0))
        screen.blit(text_surface1, (self.x + 120 + self.centering_offset, (self.y-7)))
        text_surface = basic_font.render("On" if self.state else "Off", True, (0, 0, 0))
        screen.blit(text_surface, (self.togl_head.centerx - text_surface.get_width()/2, self.y + self.h/4 - text_surface.get_height()/2))

        # pygame.draw.rect(surface, (100, 255, 100), pygame.Rect(self.x+self.radius-self.togl_head.width/2, self.y, self.togl_head.w - self.radius + 120 + text_surface1.get_width(), self.h/5))
        # pygame.draw.rect(surface, (100, 255, 100), pygame.Rect(self.x+self.radius-self.togl_head.width/2, self.y,self.togl_head.width/2 - self.radius + 120 + self.biggest_text, self.h/5))
        # pygame.draw.rect(surface, (100, 100, 255), pygame.Rect(self.x, self.y + 20,self.w, self.h/5))

class Warning:
    def __init__(self, text, position=(40, HEIGHT-80, WIDTH-80), level="warning", counter=180):

        WARNING_COLOR_PALETTE = {
            "info" : (155, 255, 200),
            "warning" : (255, 150, 130),
            "error" : (200, 50 ,50)
        }

        self.text = text
        self.dest = position[1]
        self.y = HEIGHT + 50
        self.level = level
        self.color = WARNING_COLOR_PALETTE[self.level]
        self.coloraccent = ((self.color[0] - 80), (self.color[1] - 80),(self.color[2] - 80))

        for i in range(len(self.coloraccent)):
            if self.coloraccent[i] < 0:
                self.coloraccent = (self.coloraccent[0] if i != 0 else 0, self.coloraccent[1] if i != 1 else 0, self.coloraccent[2] if i != 2 else 0)


        self.counter = counter
        self.death = False
        self.warning_text = basic_font.render(self.text, True, self.color)
        self.x = WIDTH/2 - (self.warning_text.get_width() + 15)/2
        self.velocity = 0

        self.spr_force = 0.2
        self.spr_damp  = 0.4


    def get_circle_vertex_pos(self, x, y, poly_count, radius, counter, max, min):

        progress = (counter-min) / (max-min) * poly_count
        progress = math.ceil(progress)
        result = [(x, y)]
        for i in range(progress) :
            newx = math.cos((2*math.pi*i)/poly_count) * radius
            newy = math.sin((2*math.pi*i)/poly_count) * radius

            result.append((newx + x, newy + y))
        result.append((x, y))
        result.append((x, y))
        return result
    
    def tick(self):

        
        pygame.draw.rect(screen, self.coloraccent, pygame.Rect(self.x - 20, self.y, (self.warning_text.get_width() + 15) + 40, 52), border_radius=20)

        screen.blit(self.warning_text , (self.x + 30/2 + 10, self.y))
        
        #pygame.draw.circle(screen, self.color, (self.x, self.y + 26), 15)

        pygame.draw.polygon(screen, self.color, self.get_circle_vertex_pos(self.x + 5, self.y + 26, 50, 10, self.counter if self.counter < 180 - 30 else 180 - 30, 180 - 30, 30))


        offset = self.dest - self.y
        self.velocity += offset * self.spr_force - self.velocity * self.spr_damp
        if abs(offset) < 0.5 and self.velocity < 0.0008:
            self.velocity = 0
        self.y += self.velocity

        if self.counter < 20:
            self.spr_damp = 0.4
            self.spr_force = 0.1
            self.dest = HEIGHT + 50
            self.warning_text.set_alpha(255 - i*255/5)

        self.counter -= 1
        if self.counter < 1:
            self.death = True

class Textinput:
    def __init__(self, x, y, w, h, radius, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.radius = radius
        self.color = color
        self.text = ""
        self.focused = False
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    
    def draw(self):
        
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if not self.focused:    
            pygame.draw.rect(screen, (self.color[0] , self.color[1], self.color[2]), self.rect, border_radius=self.radius)
        else:
            pygame.draw.rect(screen, (self.color[0] - 50 if (self.color[0] - 50) > 0 else 0, self.color[1] - 50 if (self.color[0] - 50) > 0 else 0, self.color[2] - 50 if (self.color[0] - 50) > 0 else 0), self.rect, border_radius=self.radius)
        
        for event in events:   
            if self.focused:      
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key == pygame.K_DELETE:
                        self.text = ""                        
                    elif event.unicode in CHARS:
                        self.text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.focused = True
                else:
                    #self.focused = False
                    pass

        text_text = basic_font.render(self.text, True, (10, 10 ,10))
        screen.blit(text_text, (self.x + 5, self.y + 5))
        




if DEBUG:
    button1 = Button(100, 100, 200, 80, (100, 100, 100), "Button 1", radius=20)


# ╭---------------------------------------------------------------------╮
# |      ╭----   ╭----╮ ╭-╮╭-╮ ╭----     ╭     ╭----╮ ╭----╮ ╭----╮     |
# |      |       |    | | ╰╯ | |         |     |    | |    | |    |     |
# |      |    ╮  |----| |    | |--       |     |    | |    | |----╯     |
# |      |    |  |    | |    | |         |     |    | |    | |          |
# |      ╰----╯  ╰    ╯ ╰    ╯ ╰----     ╰---╯ ╰----╯ ╰----╯ ╰          |
# ╰---------------------------------------------------------------------╯

def skip(silent=False, skip_song=False, simple_update=False):
        global step
        global song_counter
        global queue
        global current_song
        global curr_screen
        if not simple_update:
            set_position(0)
        step += 1
        if step > len(STEMS) or skip_song:
            step = 1

            # update the correct blacklist
            with open(f"{PROJECT_DIR}/{SCRIPT_DIR}/Blacklists.txt", "r") as f:
                txt = f.read()
            txts=txt.splitlines()
            buffer = ""
            for i in range(len(txts)):
                if i == curr_blacklist:
                    buffer += txts[i] + current_song + " " + "\n"
                else:
                    buffer += txts[i] + "\n"
            with open(f"{PROJECT_DIR}/{SCRIPT_DIR}/Blacklists.txt", "w") as f:
                f.write(buffer)
            blacklists[curr_blacklist].append(current_song)
                
            song_counter += 1
            if not silent:
                warnings.append(Warning(f"song was {sanitize(current_song)}", (40, HEIGHT-80, WIDTH-80), "info"))
            print("song counter", song_counter, "queue: ", queue)
            if song_counter > len(queue):
                warnings.append(Warning(f"you finished the playlist!", (40, HEIGHT-80, WIDTH-80), "info"))
                curr_screen = "playlists"
            else:
                print("song counter", song_counter)
                current_song = queue[song_counter - 1]
                load_song(STEMS_FOLDER + "/" +  current_song)
            print(curr_screen)
            



def debug():
    # text test
    text_surface = basic_font.render("fps: " + str(int(clock.get_fps())), True, (10, 10 ,10))
    screen.blit(text_surface, (0,5))
    
    #button test
    if button1.is_clicked() == 1:
        button_state_surf = basic_font.render('Button 1 clicked!', True, (10, 10 ,10))
    else:
        button_state_surf = basic_font.render('Button 1 not clicked', True, (10, 10 ,10))
    screen.blit(button_state_surf, (50, 200))
    button1.draw(screen)

def setup():
    global curr_screen
    global shadow_offset
    global blacklists
    global curr_blacklist

    if blacklists == "no_blacklist":
        pass
    shadow_offset = 10
    curr_screen = "main_menu_setup"

def main_menu_setup():
    global playlist_select_button
    global manage_blacklist_button  
    global curr_screen
    playlist_select_button = Button(100, 100, 200, 80, (100, 100, 100), "play bandle from Playlist", radius=20)
    manage_blacklist_button = Button(100, 200, 200, 80, (100, 100, 100), "manage blacklist", radius=20)
    curr_screen = "main_menu"

def main_menu():
    global shadow_offset
    global playlist_select_button
    global curr_screen
    global manage_blacklist_button

    manage_blacklist_button.draw(screen)
    playlist_select_button.draw(screen)
    if playlist_select_button.is_clicked():
        curr_screen = "playlists_setup"
    if manage_blacklist_button.is_clicked():
        curr_screen = "manage_blacklist_setup"

def manage_blacklist_setup():
    global go_back_button
    global curr_screen
    global close_button
    global wiki
    global wiki_bool
    global blacklist_buttons

    wiki_bool = True

    go_back_button = Button(20, 20, 100, 50, (200, 100, 100), "Back", radius=15)
    close_button = Button(WIDTH-40, 150-20, 40, 40, (250 ,250 ,250), "x", 20)
    curr_screen = "manage_blacklist"
    blacklist_buttons = []


    for i in range(len(blacklist_names)):
        blacklist_buttons.append(Button(70, 170 + i*70, WIDTH-140, 60, (200, 200, 200), blacklist_names[i], 20))


    wiki = []
    wiki.append("The selected blacklist will")
    wiki.append("remember the songs you played")
    wiki.append("so you dont get them twice.")
    wiki.append("")
    wiki.append("Manage them as you wish!")
    wiki.append("you can also directly edit")
    wiki.append("\"Blacklists.txt\" for more control")

def manage_blacklist():
    global shadow_offset
    global go_back_button
    global curr_screen
    global wiki
    global wiki_bool
    global close_button
    global manage_blacklist_button
    global curr_blacklist

    pygame.draw.rect(screen, (230, 160, 160), pygame.Rect(0, -50, WIDTH, 145))
    

    if wiki_bool:
        pygame.draw.rect(screen, (190, 180, 170), pygame.Rect(20, 130, WIDTH-40, 270), border_radius=20)
        for i in range(len(wiki)):
            screen.blit(small_font.render(wiki[i], True, (10, 10, 10)), (45, 130 + 20 + 30*i))

        
        close_button.draw(screen)

        if close_button.is_clicked():
            wiki_bool = False

    offset = 10
    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(50 + offset, (wiki_bool * 270) + 150 + offset, WIDTH - 100, 450 - (wiki_bool * 270)), border_radius=20)
    pygame.draw.rect(screen, (240, 240, 240), pygame.Rect(50, (wiki_bool * 270) + 150, WIDTH - 100, 450 - (wiki_bool * 270)), border_radius=20)

    for i in range(len(blacklist_buttons)):

        blacklist_buttons[i].y = i*70 + 170 + (wiki_bool * 270)
        if blacklist_buttons[i].is_clicked():
            curr_blacklist = i
        if curr_blacklist == i:
            blacklist_buttons[i].color = (100, 200, 100)
        else:
            blacklist_buttons[i].color = (200, 200, 200)
        blacklist_buttons[i].draw(screen)


    go_back_button.draw(screen)
    if go_back_button.is_clicked() == 1:
        curr_screen = "main_menu"

    



def playlist_select_setup():
    global selected_p
    global buttons
    global selected_playlist
    global curr_screen
    global start_button
    global CHEAT_MODE_toggle
    global CHEAT_MODE
    global go_back_button

    
    selected_p = -1
    buttons = []
    selected_playlist = ""
    
    start_button = Button(WIDTH/2 - 100, 780, 200, 80, (100, 200, 100), "Start", radius=20, click_counter=20)

    go_back_button = Button(20, 20, 100, 50, (200, 100, 100), "Back", radius=15)

    CHEAT_MODE_toggle = Toggle(WIDTH/2 - 200, 670, 400, 65, (100, 200, 100), (200, 100, 100), "CHEAT MODE: ON", "CHEAT MODE: OFF", radius=20)
    CHEAT_MODE = CHEAT_MODE_toggle.state


    for i in range(len(playlists)):
        buttons.append(Button(71, 250 + i*60, WIDTH - 142, 48, (200, 200, 200), playlist_to_names[playlists[i]], radius=15))
    curr_screen = "playlists"

def playlist_select():
    global shadow_offset
    global curr_screen
    global CHEAT_MODE
    global buttons
    global selected_playlist
    global selected_p
    global start_button
    global CHEAT_MODE_toggle
    global go_back_button

    
    # draw cheat mode toggle
    CHEAT_MODE_toggle.draw(screen)
    CHEAT_MODE = CHEAT_MODE_toggle.state

    pygame.draw.rect(screen, (230, 160, 160), pygame.Rect(0, -50, WIDTH, 145))

    go_back_button.draw(screen)
    if go_back_button.is_clicked() == 1:
        curr_screen = "main_menu"

    # title text
    text_surface = title_font.render("Select playlist", True, (10, 10 ,10))
    screen.blit(text_surface, (WIDTH/2 - text_surface.get_width()/2,120))

    # background box
    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(50 + shadow_offset, 230 + shadow_offset, WIDTH - 100, 400), border_radius=20)
    pygame.draw.rect(screen, (240, 240, 240), pygame.Rect(50, 230, WIDTH - 100, 400), border_radius=20)
    

    # check who is selected
    for i in range(len(buttons)):
        if buttons[i].is_clicked():
            selected_p = i
            selected_playlist = name_to_playlists[buttons[i].text]
    # draw buttons
    for i in range(len(buttons)):
        if i == selected_p:
            buttons[i].color = (100, 200, 100)
        else:
            buttons[i].color = (200, 200, 200)
        buttons[i].draw(screen)


    
    
    pygame.draw.rect(screen, (50, 100, 50), pygame.Rect(start_button.x + shadow_offset, start_button.y + shadow_offset, start_button.w, start_button.h), border_radius=20)
    start_button.draw(screen)

    if start_button.is_clicked() == 1:  
        if selected_playlist != "":
            curr_screen = "bandle_setup"
        else:
            warnings.append( Warning("you need to select a playlist", (40, HEIGHT-80, WIDTH-80), level="warning"))

def bandle_setup():
    global curr_screen
    global current_song
    global queue
    global step
    global song_counter
    global bandle_guessing_counter
    global text
    global selected
    global offset
    global scrolling

    global skip_button
    global go_back_button
    global play_button
    global guess_button
    global skip_ahead
    global skip_ahead_img
    global rewind
    global rewind_img
    global textinput
    
    global skip
    
    

        


    # setting vars
    step = 1
    song_counter = 1
    bandle_guessing_counter = 0
    text = ""
    selected = -1
    offset = 0
    scrolling = False

    # setting buttons
    
    go_back_button = Button(20, 20, 100, 50, (200, 100, 100), "Back", radius=15)


    play_button  = Button(WIDTH/2 - 45       , HEIGHT -210, 90 , 85 , (100, 200, 100), "Play"      , radius=20, click_counter=20)
    skip_button  = Button(WIDTH/2 + 135      , HEIGHT -210, 90 , 85 , (200, 100, 100), "Skip"      , radius=20, click_counter=20)
    guess_button = Button(WIDTH/2 - 135 -90  , HEIGHT -210, 90 , 85 , (100, 100, 200), "Guess", radius=15, click_counter=20)

    rewind =     Button(WIDTH/2 - 45 -90  , HEIGHT -210, 90 , 85 , "red", ""      , radius=20, click_counter=20)
    skip_ahead = Button(WIDTH/2 + 45      , HEIGHT -210, 90 , 85 , "red", ""      , radius=20, click_counter=20)
    
    skip_ahead_img = pygame.image.load(PROJECT_DIR+"/"+ SCRIPT_DIR + "/assets/skip_ahead.png").convert_alpha()
    skip_ahead_img = pygame.transform.smoothscale(skip_ahead_img, (60, 60))

    rewind_img = pygame.image.load(PROJECT_DIR+"/"+ SCRIPT_DIR + "/assets/rewind.png").convert_alpha()
    rewind_img = pygame.transform.smoothscale(rewind_img, (60, 60))

    textinput = Textinput(25, HEIGHT, WIDTH-50, 60, 20, (200, 200, 200))

                 
        

    # preparing song queue
    queue = playlist_to_songs[selected_playlist]
    print(queue)
    bfr = []
    for i in range(len(queue)):
        print(queue[i])
        print(blacklists[curr_blacklist])
        print(queue[i] in blacklists[curr_blacklist])
        if queue[i] in blacklists[curr_blacklist]:
            bfr.append(i)
    print(queue)
    for i in range(len(bfr)):
        queue.pop(bfr[i] - i)
    print(blacklists[curr_blacklist])
    print(bfr)
    print(queue)

    if queue == []:
        curr_screen = "playlists"
        warnings.append( Warning("already finished this playlist", (40, HEIGHT-80, WIDTH-80), level="warning"))
    else:
        random.shuffle(queue)
        current_song = queue[0]
        load_song(STEMS_FOLDER + "/" +  current_song)
        curr_screen = "bandle"
    

def bandle_screen():
    global shadow_offset
    global curr_screen
    global step
    global song_counter
    global current_song
    global bandle_guessing_counter
    global offset
    global selected
    global skip_ahead_img
    global rewind_img
    global vlc_on_end_sig
    global mouse_x
    global mouse_y
    global scrolling

    global skip_button
    global go_back_button
    global play_button
    global skip_ahead
    global rewind
    global textinput

    global skip

    #deal with players
    if str(players[0].get_state()) in ["State.Playing", "State.Paused"]:
        progression = players[0].get_time()/players[0].get_length() if players[0].get_length() != 0 else 1
    else:
        progression = 0
    if vlc_on_end_sig:
        vlc_on_end_sig = False
        load_song(STEMS_FOLDER + "/" +  current_song)
        play_step()



    pygame.draw.rect(screen, (230, 160, 160), pygame.Rect(0, -50, WIDTH, 145))

    # title text
    bandle_title = title_font.render("Bandle", True, (10, 10 ,10))
    screen.blit(bandle_title, (WIDTH/2 - bandle_title.get_width()/2,120))
    
    
    
    # selected playlist text (cool little script)
    selected_playlist_text = f"Selected playlist: {playlist_to_names[selected_playlist]}"
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
        selected_playlist_text = small_font.render(wordlines[i], True, (105, 105, 105))
        screen.blit(selected_playlist_text, (WIDTH/2 + 55 - selected_playlist_text.get_width()/2,20 + go_back_button.h/2 - 18 - (len(wordlines)-1)*30/2 + i*30))

    
    # cheat mode display
    if CHEAT_MODE:
        song_text = basic_font.render(f"Current song: {current_song}, ya little CHEATER", True, (10, 10 ,10))
        screen.blit(song_text, (50, 200))

    # draw stem rectangles
    for i in range(len(STEMS)):
        pygame.draw.rect(screen, (200, 200, 200) if i < step else (150, 150, 150), pygame.Rect(50, 245 + i*75, WIDTH - 100, 60), border_radius=15)
        stem_text = basic_font.render(f"{STEMS[i]}", True, (10, 10 ,10))
        screen.blit(stem_text, (WIDTH/2 - stem_text.get_width()/2, 249 + i*75))


    # guess button
    if curr_screen != "bandle_stare":
        guess_button.draw(screen)
        if guess_button.is_clicked() == 1:
            if curr_screen != "bandle_guessing":
                curr_screen = "bandle_guessing"
                offset = 0
                bandle_guessing_counter = 0
                textinput.focused = True
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and curr_screen == "bandle_guessing":
                my = pygame.mouse.get_pos()[1]
                if my < HEIGHT - 500:
                    curr_screen = "bandle"
    else:
        guess_button.draw(screen, (150, 150, 150))
        if guess_button.is_clicked() == 1:
            warnings.append(Warning("cannot guess in admire mode", level="warning"))
    


    # naviagtion
    
    skip_ahead.draw(screen)
    if skip_ahead.is_clicked():
        offset_players(5000)

    screen.blit(skip_ahead_img, (WIDTH/2 + 90 -30  , HEIGHT -195))

    rewind.draw(screen)
    if rewind.is_clicked():
        offset_players(-5000)

    screen.blit(rewind_img, (WIDTH/2 - 90 -30  , HEIGHT -195))

    # progression bar

    pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(WIDTH/2-120, 890, 240, 10), border_radius=5)
    pygame.draw.circle(screen, (200, 200, 200), (WIDTH/2-115 + 230*(progression), 895), 5)

    # progress bar hitbox visualizer1
    # pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(WIDTH/2-120, 870, 240, 110))
    # pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(WIDTH/2+120, 870, 100, 110))
    # pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(WIDTH/2-220, 870, 100, 110))


    if pygame.mouse.get_pressed()[0]:
        if mouse_y > 870 and mouse_y < 870+110 and mouse_x > WIDTH/2-220 and mouse_x < WIDTH/2+220:
            if mouse_x > WIDTH/2-120:
                if mouse_x > WIDTH/2+120:
                    set_position(1)
                    scrolling = True
                else:
                    set_position((mouse_x - (WIDTH/2-120))/240)
                    scrolling = True
            else:
                set_position(0)
                scrolling = True
    else:
        if scrolling:
            scrolling = not scrolling
    
    if scrolling:
        if players[0].is_playing():
            pause()

    # go back button
    go_back_button.draw(screen)
    if go_back_button.is_clicked() == 1 and curr_screen != "bandle_guessing":
        curr_screen = "playlists"

    # skip button
    skip_button.draw(screen)
    if skip_button.is_clicked() == 1 and curr_screen != "bandle_guessing":
        skip(True if curr_screen == "bandle_stare" else False, True if curr_screen == "bandle_stare" else False)
        if curr_screen != "playlists":
            curr_screen = "bandle"
        

    # play/pause button
    # make the button change depending on state
    if  not players[0].is_playing():
        play_button.text = "Play"
        play_button.draw(screen)
    else:
        play_button.text = "Pause"
        play_button.draw(screen)

    if play_button.is_clicked() == 1 and curr_screen != "bandle_guessing":
        
        if not players[0].is_playing():
            if players[0].get_time() >= players[0].get_length():
                set_position(0)
                play_step()
            else:
                play_step()
        else:
            pause()
            
    set_volume(step)

    if curr_screen == "bandle_guessing":
            
        # slight blur
        s = pygame.Surface((1000,1000))  
        s.set_alpha(bandle_guessing_counter * 128)             
        s.fill((100,100,100))           
        screen.blit(s, (0,0))  

        #popup
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, HEIGHT - (500/0.5)*bandle_guessing_counter if bandle_guessing_counter < 0.5 else HEIGHT - 500, WIDTH, 600), border_radius=20)
        
        textinput.y = HEIGHT + 30 - (500/0.5)*bandle_guessing_counter if bandle_guessing_counter < 0.5 else HEIGHT + 30 - 500
        textinput.draw()
        

        limit = 5
        text = textinput.text
        suggestions = []
        actual_suggestions = []
        for i in range(len(all_songs_sanitized)):
            if text.lower() in all_songs_sanitized[i].lower():
                if all_songs_sanitized[i] not in suggestions:
                    suggestions.append(all_songs_sanitized[i])
                    actual_suggestions.append(all_songs[i])

        

        for event in events:
            if event.type == pygame.KEYDOWN:
                if textinput.focused:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_DOWN:
                        textinput.focused = False
                        selected = 0

                else:
                    if event.key == pygame.K_DOWN:
                        selected += 1
                    if event.key == pygame.K_UP:
                        selected -= 1
                    if event.key == pygame.K_RETURN:
                        #guess
                        guess = actual_suggestions[selected]
                        # print(f"you guessed: {guess}, correct would be {current_song}")
                        if guess == current_song:
                            curr_screen = "bandle_win"
                        else: 
                            warnings.append(Warning("nope", (40, HEIGHT-80, WIDTH-80), "info"))
                            skip()
                            curr_screen = "bandle"
                        

                if event.key == pygame.K_ESCAPE:
                    curr_screen = "bandle"

        if selected > len(suggestions) - 1:
            selected = 0
        elif selected < 0:
            selected = -1
            textinput.focused = True
       
        if selected >  offset + limit - 2:
            offset += 1
        elif selected < offset:
            offset -= 1
        
        if offset < 0:
            offset = 0
        elif offset > len(suggestions) - 1 - limit:
            offset = (len(suggestions) - 1 - limit) if (len(suggestions) - 1 - limit) > 0 else 0
            
        suggestions = suggestions[offset:offset + limit]


        if selected != -1:
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(50, 600 + (selected-offset)*50, 100, 30), border_radius=20)

        for i in suggestions:
            suggestion_surf = basic_font.render(i, True, (10, 10 ,10))
            screen.blit(suggestion_surf, (50, HEIGHT + 100 + suggestions.index(i)*40 - (500/0.5)*bandle_guessing_counter if bandle_guessing_counter < 0.5 else HEIGHT + 100 + suggestions.index(i)*40 - 500))

        bandle_guessing_counter += 1/30
        if bandle_guessing_counter > 1:
            bandle_guessing_counter = 1

    if curr_screen == "bandle_win":
        
        s = pygame.Surface((1000,1000))  
        s.set_alpha(bandle_guessing_counter * 128)             
        s.fill((100,100,100))           
        screen.blit(s, (0,0)) 

        pygame.draw.rect(screen, (230, 230, 230), pygame.Rect(WIDTH/2-225, HEIGHT/2 -225, 450, 450), border_radius=20)
        win_text = title_font.render("YOU WON", True, (10, 10, 10))
        screen.blit(win_text, (WIDTH/2 - win_text.get_width()/2, HEIGHT/2 - 200))

        butt = Button(WIDTH/2-100, HEIGHT/2-100, 200, 40, (155, 155, 155), "go back and admire", 20)
        butt.draw(screen)
        if butt.is_clicked():
            curr_screen = "bandle_stare"
        
        next = Button(WIDTH/2-100, HEIGHT/2-0, 200, 40, (155, 155, 155), "go next", 20)
        next.draw(screen)

        if next.is_clicked():
            skip(True, True)
            curr_screen = "bandle"

    if curr_screen == "bandle_stare":
        stems = []
        for i in range(len(STEMS)):
            
            stems.append(Button(50, 245 + i*75, WIDTH - 100, 60, (200, 200, 200) if i < step else (150, 150, 150), f"{STEMS[i]}", 15))
            stems[i].draw(screen)

            if stems[i].is_clicked():
                step = i
                skip(True, simple_update=True)
            # pygame.draw.rect(screen, (200, 200, 200) if i < step else (150, 150, 150), pygame.Rect(50, 250 + i*80, WIDTH - 100, 60), border_radius=15)
            # stem_text = basic_font.render(f"{STEMS[i]}", True, (10, 10 ,10))
            # screen.blit(stem_text, (WIDTH/2 - stem_text.get_width()/2, 254 + i*80))












counter = 0
curr_screen = "setup"
warnings = []

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    screen.fill("pink")  # fill screen with pink

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            event.pos = scale_mouse_pos(event.pos)
            mouse_x, mouse_y = event.pos[:]



    if DEBUG == True:
        debug()
    elif curr_screen == "main_menu_setup":
        main_menu_setup()
    elif curr_screen == "main_menu":
        main_menu()
    elif curr_screen == "manage_blacklist_setup":
        manage_blacklist_setup()
    elif curr_screen == "manage_blacklist":
        manage_blacklist()
    elif curr_screen == "playlists_setup":
        playlist_select_setup()
    elif curr_screen == "setup":
        setup()
    elif curr_screen == "playlists":
        playlist_select()
    elif curr_screen == "bandle_setup":
        bandle_setup()
    elif curr_screen == "bandle" or curr_screen == "bandle_guessing" or curr_screen == "bandle_win" or curr_screen == "bandle_stare":
        bandle_screen()
        
    for i in range(len(warnings)-1, -1, -1):
        warnings[i].tick()
        if warnings[i].death:
            warnings.pop(i)

    # flip() the display to put your work on screen
    scaled = pygame.transform.smoothscale(
        screen,
        window.get_size()
    )

    window.blit(scaled, (0, 0))
    if CF_DEBUG_VLC:
        debug_vlc()

    pygame.display.flip()
    pygame.event.clear()  # clear event queuem
    clock.tick(60)  # limits FPS to 60
    counter += 1

pygame.quit()







