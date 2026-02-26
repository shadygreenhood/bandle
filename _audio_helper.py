from pydub import AudioSegment
import simpleaudio as sa
from time import sleep, perf_counter
import math
from pathlib import Path
import matplotlib.pyplot as plt

if __name__ == "__main__":    
    #constants
    STEMS = ["drums", "bass", "guitar", "piano", "other", "vocals"]
    SEPERATED_DIR = r"c:\Users\REMOVED_USERNAME\Documents\github projects\split"

# ╭----------------------------------------╮
# |      ╭----╮  ╭    ╮ ╭--.  ╭---╮ ╭----╮ |
# |      |    |  |    | |   ¡   |   |    | |
# |      ╞----╡  |    | |   |   |   |    | |
# |      |    |  |    | |   !  _|_  |    | |
# |      ╰    ╯  ╰----╯ ╰--'  ╰---╯ ╰----╯ |
# ╰----------------------------------------╯


#
#   README
#
#   Player_obj intended behaviour:
#
#   first init in an undefined state
#   each time curr_song changes or is defined, use load(curr_song) to prepare player to play (pointer is reset)
#   use play(step) to play a specific step's audio from the beginning
#   use update_to_play(step) to play a specific step's audio from the pointer's location
#   use toggle() to either play or pause current playback
#   use stop_all() to stop playback (like when leaving the bandle screen)
#   use update_volume() to update volume without stopping playback
#   use frame() after each frame to loop playback if needed, and do all sorts of updates
#   use is_playing() to check if player is either ["Undefined", "Playing", "Paused", "Stopped"]
#
#   audio holding vars are split into two categories:
#    - _raw_     : holds elemental data that hasnt been overly doctored to a specific use
#    - _baked_   : holds doctored data that was meant to optimize a specific task
#    - _temp_    : holds temporary or intermediate data with no value outside of its context
#
#   important vars:
#    - STEMS                : a list of available stem categories that sum up to the full original song
#    - _raw_stems           : dict that associates a STEM entry to its pydub waveobject, needs to be updated on every song change
#    - _baked_step_audios   : a dict holding overlayed waveobjects for every stem, meant to be the final bandle audio for each step, needs to be updated on every song change 
#    - pointer              : stores info of where we are in the playback
#    - _temp_curr_audio     : raw audio sent to simlpeaudio buffer to be played, very low level
#
#
#

class Player_obj:
    def __init__(self, volume=100):
        
        # low level simpleaudio stuff
        self._temp_curr_audio   = None
        self.pointer            = 0
        self.play_obj           = None
        self.start_pointer      = 0
        self.previous_pointer   = 0

        # high level bandle project utilities
        self._raw_stems         = []
        self._baked_step_audios = []
        self.status     = "Undefined"
        self.curr_step          = 0
        self.audio_len          = 0
        self.volume             = volume
        self.track              = ""

    # small helper for load() (_raw_stems has to be defined)
    def overlay_step(self, step):
        _temp_step_track = self._raw_stems[STEMS[0]]
        for i in range(step-1):
            _temp_step_track = AudioSegment.overlay(_temp_step_track, self._raw_stems[STEMS[i+1]])
        return _temp_step_track


    def load(self, track):
        self.track = track
        if Path(SEPERATED_DIR + "\\htdemucs_6s\\" + track).exists:

            try:   
                # defining _raw_stems
                self._raw_stems = { STEMS[i]: (AudioSegment.from_wav(SEPERATED_DIR + "\\htdemucs_6s\\" + track + "\\" + STEMS[i] + ".wav")) for i in range(len(STEMS))}
                
                # defining _baked_step_audios
                self._baked_step_audios = [self.overlay_step(i) for i in range(1, len(STEMS)+1)]

                self.audio_len = len(self._baked_step_audios[0])

                self.status = "Stopped"

                self.curr_step = 0

            except Exception as e:
                print(f"failed to read some stems, {e}")
        else:
            print("couldnt find specified song's folder")


    def analyse_audio(self, curious_audio=""):
        if self.track != "" and self.status != "Undefined":
            print(self.track)

            silent_stems = []
            for i in range(len(STEMS)):
                if self._raw_stems[STEMS[i]].dBFS < -30:
                    silent_stems.append(STEMS[i])
            print(silent_stems)

            first_lack_of_silence = []
            precision = 1000 * self._raw_stems[STEMS[0]].channels   # needs to be doubled if audio is stereo
            for j in range(len(STEMS)):
                
                for i in range(math.floor(self.audio_len/precision) - 1):
                    silence_value = self._raw_stems[STEMS[j]][i*precision:(i+1)*precision].dBFS
                    if silence_value > -30:
                        first_lack_of_silence.append(i*precision/self._raw_stems[STEMS[0]].channels)
                        break
                if len(first_lack_of_silence) < j+1:
                    first_lack_of_silence.append("never")
            print(first_lack_of_silence)

            for i in range(len(STEMS)):
                if STEMS[i] in silent_stems:
                    first_lack_of_silence[i] = "muted" if first_lack_of_silence[i] != "never" else "never"
            print(first_lack_of_silence)


            if curious_audio != "" and curious_audio in STEMS: # for debug purposes
                curious_stem = curious_audio

                print(f"dBFS value: {self._raw_stems[curious_stem].dBFS}")
                
                simplified_chart = []
                for i in range(math.floor(self.audio_len/precision) - 1):
                    silence_value = self._raw_stems[curious_stem][i*precision:(i+1)*precision].dBFS
                    simplified_chart.append(silence_value)
                
                fig, ax = plt.subplots()
                ax.plot(simplified_chart)
                playhead = ax.axvline(0, linestyle="--")
                plt.ion()
                plt.show()

                duration_sec = self.audio_len / 1000
                start_time = perf_counter()
                self.stop_all
                self.play(STEMS.index(curious_stem) + 1)
                while True:
                    current_time = perf_counter() - start_time
                    if current_time > duration_sec:
                        break

                    playhead.set_xdata([current_time*2])
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    action = input("[c]ancel, [u]pdate_to_play, [t]oggle, update_[v]olume, st[a]tus, [p]lay")
                    if action == "c":
                        break
                    elif action == "u":
                        player.update_to_play(int(input("step:")))
                    elif action == "t":
                        player.toggle()
                    elif action == "v":
                        player.update_volume(int(input("volume")))
                    elif action == "a":
                        print(player.is_playing_var)
                    elif action == "p":
                        player.play(int(input("step?")))
                    player.frame()





    
    def play(self, step):
        if self.status != "Undefined":
            self.curr_step = step
            self.previous_pointer = 0
            self.start_pointer = perf_counter()
            dB = 20 * math.log10(self.volume/100)
            self._temp_curr_audio = self._baked_step_audios[step-1] + dB

            self.play_obj = sa.play_buffer(
                self._temp_curr_audio.raw_data,
                num_channels=self._temp_curr_audio.channels,
                bytes_per_sample=self._temp_curr_audio.sample_width,
                sample_rate=self._temp_curr_audio.frame_rate
            )

            self.status = "Playing"

    def update_to_play(self, step):

        if self.status == "Stopped":
            self.play(step)

        elif self.status == "Paused":
            self.curr_step = step
            self.toggle()
        
        elif self.status == "Playing":
            if self.pointer * 1000 < self.audio_len:
                self.curr_step = step
                self.update_pointer()
                dB = 20 * math.log10(self.volume/100)
                self._temp_curr_audio = self._baked_step_audios[step-1][self.pointer*1000:] + dB
                
                self.play_obj.stop()
                self.play_obj = sa.play_buffer(
                    self._temp_curr_audio.raw_data,
                    num_channels=self._temp_curr_audio.channels,
                    bytes_per_sample=self._temp_curr_audio.sample_width,
                    sample_rate=self._temp_curr_audio.frame_rate
                )

                self.status = "Playing"
            else:
                self.play(self.curr_step)

    def toggle(self):
        if self.status == "Playing":
            self.update_pointer()
            self.previous_pointer = self.pointer
            self.play_obj.stop()
            self.status = "Paused"
        elif self.status == "Paused":
            if self.pointer * 1000 < self.audio_len:
                self.start_pointer = perf_counter()
                self.update_pointer()
                dB = 20 * math.log10(self.volume/100)
                self._temp_curr_audio = self._baked_step_audios[self.curr_step-1][self.pointer*1000:] + dB

                self.play_obj = sa.play_buffer(
                    self._temp_curr_audio.raw_data,
                    num_channels=self._temp_curr_audio.channels,
                    bytes_per_sample=self._temp_curr_audio.sample_width,
                    sample_rate=self._temp_curr_audio.frame_rate
                )

                self.status = "Playing"
            else:
                self.play(self.curr_step)
        elif self.status == "Stopped":
            if self.curr_step != 0:
                self.play(self.curr_step)

    def stop_all(self):
        self.play_obj.stop()
        self.status = "Stopped"
        self.curr_step = 0
        self.pointer = 0
        self.previous_pointer = 0
        self.start_pointer = 0

    def update_volume(self, volume):
        if self.status == "Playing":
            # preparing buffer
            dB = 20 * math.log10(volume/100)

            # hot swapping buffer
            self.update_pointer()
            self._temp_curr_audio = self._baked_step_audios[self.curr_step-1][self.pointer*1000:] + dB
            self.play_obj.stop()

            self.play_obj = sa.play_buffer(
                self._temp_curr_audio.raw_data,
                num_channels=self._temp_curr_audio.channels,
                bytes_per_sample=self._temp_curr_audio.sample_width,
                sample_rate=self._temp_curr_audio.frame_rate
            )

        else:
            self.volume = volume/100


    def frame(self):
        print(f"len:{self.audio_len}, step:{self.curr_step}, pointer:{self.pointer}, prev:{self.previous_pointer}, start:{self.start_pointer}, status:{self.status}, vol:{self.volume}")
        self.update_pointer()
        if self.status == "Playing":
            if self.pointer * 1000 > self.audio_len:
                self.play(self.curr_step)


    def is_playing(self):
        # can be one of ["Undefined", "Playing", "Paused", "Stopped"]
        return self.status
    
    def update_pointer(self):
        if self.status == "Paused":
            pass
        elif self.status == "Playing":
            self.pointer = perf_counter() - self.start_pointer + self.previous_pointer
        elif self.status == "Stopped":
            self.pointer = 0






if __name__ == "__main__":
    player = Player_obj()
    #vars
    curr_song = "The Sound of Silence"

    while True:
        action = input("[s]top_all, [u]pdate_to_play, [t]oggle, update_[v]olume, [i]s_playing, [l]oad, p[o]inter, st[a]tus, [p]lay, a[n]alyse")
        if action == "s":
            player.stop_all()
        elif action == "u":
            player.update_to_play(int(input("step:")))
        elif action == "t":
            player.toggle()
        elif action == "v":
            player.update_volume(int(input("volume")))
        elif action == "i":
            print(player.is_playing())
        elif action == "l":
            player.load(input("curr_song?"))
        elif action == "o":
            player.update_pointer()
            print(player.pointer)
        elif action == "a":
            print(player.is_playing_var)
        elif action == "p":
            player.play(int(input("step?")))
        elif action == "n":
            player.analyse_audio(input("curious audio?"))
        player.frame()