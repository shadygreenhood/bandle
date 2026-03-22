from pydub import AudioSegment      # type: ignore
import simpleaudio as sa            # type: ignore
from time import sleep, perf_counter
import math
from pathlib import Path
import matplotlib.pyplot as plt     # type: ignore

if __name__ == "__main__":    
    #constants
    STEMS = ["drums", "bass", "guitar", "piano", "other", "vocals"]
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    SEPERATED_DIR = Path(BASE_DIR / "split")

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
    def __init__(self, STEMS, SEPERATED_DIR, volume=100):

        self.STEMS = STEMS
        self.SEPERATED_DIR = SEPERATED_DIR
        
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
        _temp_step_track = self._raw_stems[self.STEMS[0]]
        for i in range(step-1):
            _temp_step_track = AudioSegment.overlay(_temp_step_track, self._raw_stems[self.STEMS[i+1]])
        return _temp_step_track



# ╭------------------------------------------------------------------------------------------------------╮
# |      ╭==╮   ╭  ╮   ╭-.    .   ╭==╮         ╭==╮   ╭     ╭==╮   ╮ ╭   ╭=-.   ╭==╮   ╭=-╮   ╭  ╭       |
# |      ╞--╡   |  |   |  |   |   |  |         ╞==╯   |     ╞--╡   ╰╮╯   ╞-:╯   ╞-╡   |      ╞=:        |
# |      ╰  ╯   ╰==╯   ╰='    ╯   ╰==╯         ╰      ╰-╯   ╰  ╯    ╯    ╰=-╯   ╰  ╯   ╰=-╯   ╰  ╰       |
# ╰------------------------------------------------------------------------------------------------------╯

    def load(self, track):
        self.track = track
        if Path(self.SEPERATED_DIR / track).exists:

            try:   
                # defining _raw_stems
                self._raw_stems = { self.STEMS[i]: (AudioSegment.from_wav(self.SEPERATED_DIR / track / (self.STEMS[i] + ".wav"))) for i in range(len(self.STEMS))}
                
                # defining _baked_step_audios
                self._baked_step_audios = [self.overlay_step(i) for i in range(1, len(self.STEMS)+1)]

                self.audio_len = len(self._baked_step_audios[0])
                if self.audio_len == 0:
                    print("something went wrong...")

                self.status = "Stopped"

                self.curr_step = 0

            except Exception as e:
                print(f"failed to read some stems, {e}")
        else:
            print("couldnt find specified song's folder")


    def seek(self, pos, step=-1):
        if self.status == "Playing":
            self.toggle()
        elif self.status == "Stopped":
            if step == -1:
                pass
            else:
                self.play(step)
                self.curr_step = step
                self.toggle()
        if self.status == "Paused":
            self.previous_pointer = pos / 1000


    def offset_player(self, offset):
        if self.status == "Playing":
            self.start_pointer -= offset/1000
            self.update_pointer()
            dB = 20 * math.log10(self.volume/100)
            if self.pointer*1000 < 0 or self.pointer*1000 > self.audio_len:
                self._temp_curr_audio = self._baked_step_audios[self.curr_step-1] + dB
                self.start_pointer = perf_counter()
                self.previous_pointer = 0
            else:
                self._temp_curr_audio = self._baked_step_audios[self.curr_step-1][self.pointer*1000:] + dB

            
            self.play_obj.stop()
            self.play_obj = sa.play_buffer(
                self._temp_curr_audio.raw_data,
                num_channels=self._temp_curr_audio.channels,
                bytes_per_sample=self._temp_curr_audio.sample_width,
                sample_rate=self._temp_curr_audio.frame_rate
            )
        elif self.status == "Stopped":
            pass
        elif self.status == "Paused":
            self.pointer += offset

    def play(self, step, offset=0):
        if self.status != "Undefined":
            self.curr_step = step
            self.previous_pointer = 0
            self.start_pointer = perf_counter()
            dB = 20 * math.log10(self.volume/100)

            if offset < self.audio_len:
                self._temp_curr_audio = self._baked_step_audios[self.curr_step-1][offset:] + dB
            else:
                self._temp_curr_audio = self._baked_step_audios[self.curr_step-1] + dB
            if self.status == "Playing":
                self.play_obj.stop()
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
            self.pointer = self.previous_pointer
        elif self.status == "Playing":
            self.pointer = perf_counter() - self.start_pointer + self.previous_pointer
        elif self.status == "Stopped":
            self.pointer = 0



# ╭---------------------------------------------------------------------------------------------------╮
# |      ╭==╮   ╭  ╮   ╭-.    .   ╭==╮         ╭==╮   ╭╮ ╮   ╭==╮   ╭     ╮ ╭   ╭==╮   .   ╭==╮       |
# |      ╞--╡   |  |   |  |   |   |  |         ╞--╡   |╰╮|   ╞--╡   |     ╰╮╯   ╰--╮   |   ╰--╮       |
# |      ╰  ╯   ╰==╯   ╰='    ╯   ╰==╯         ╰  ╯   ╰ ╰╯   ╰  ╯   ╰-╯    ╯    ╰==╯   ╯   ╰==╯       |
# ╰---------------------------------------------------------------------------------------------------╯
    
    # unused
    def analyse_audio(self, simple_testing=False):
        if self.track != "" and self.status != "Undefined":
            

            # calculate a simplified version of the waveform to determine when a stem is present
            precision = 1000  # sample noise averaged over a second

            simplified_charts = { x: [] for x in self.STEMS }
            for x in self.STEMS:
                for i in range(math.floor(self.audio_len/precision) - 1):
                    silence_value = self._raw_stems[x][i*precision:(i+1)*precision].dBFS
                    simplified_charts[x].append(silence_value)
            
            if simple_testing == False:
                diagnosis = self.diagnose_audio(simplified_charts, False)
                
                compressed_diagnosis = { x : [] for x in self.STEMS }
                for x in self.STEMS:
                    previous = False
                    for i in range(len(diagnosis[x])):
                        if previous != diagnosis[x][i]:
                            compressed_diagnosis[x].append(i)
                        previous = diagnosis[x][i]
                
                btr_compression =  { x : [] for x in self.STEMS }
                for x in self.STEMS:
                    for i in range(len(compressed_diagnosis[x])):
                        if i % 2 == 0:
                            start = compressed_diagnosis[x][i]
                            btr_compression[x].append(start)
                        else:
                            duration = compressed_diagnosis[x][i]-start
                            btr_compression[x].append(duration)
                            if duration < 10: # if segment is too short, its probaly not worth saving
                                btr_compression[x].pop()
                                btr_compression[x].pop()

                

                # btr_compression returns a dict, with stems as indices, that associates info on stem presence:
                # every pair index is the start of a stem beeing audible
                # every odd index indicates the length of the previously started segment
                for x in self.STEMS:
                    if len(btr_compression[x]) % 2 == 1:
                        btr_compression[x].append(len(diagnosis[x]) - btr_compression[x][-1])


                return btr_compression


            else:
                print(self.track)
                diagnosis = self.diagnose_audio(simplified_charts, True)
                fig, ax = plt.subplots()
                while True:
                    focused_stem = self.STEMS[int(input("step?"))-1]

                    # plotting intermediate steps
                    ax.clear()
                    for i in range(len(diagnosis)):
                        ax.plot(diagnosis[i][focused_stem])
                    playhead = ax.axvline(0, linestyle="--")
                    plt.ion()
                    plt.show()

                    duration_sec = self.audio_len / 1000
                    start_time = perf_counter()
                    self.stop_all
                    self.play(self.STEMS.index(focused_stem) + 1)
                    
                    while True:
                        current_time = perf_counter() - start_time
                        if current_time > duration_sec:
                            break

                        playhead.set_xdata([current_time])
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
                    action = input("do you want to study another stem? [y/n]")
                    if action != "y":
                        plt.close()
                        break

    # unused
    def diagnose_audio(self, charts_dict, return_intermediate_steps=False):

        # removing invalid input
        cleaned_charts = { x: [] for x in self.STEMS }
        for  x in self.STEMS:    
            for i in range(len(charts_dict[x])):
                try:
                    if charts_dict[x][i] < 100 and charts_dict[x][i] > -100:
                        cleaned_charts[x].append(charts_dict[x][i])
                    else:
                        cleaned_charts[x].append(None)
                except:
                    if len(charts_dict[x]) < i + 1:
                        cleaned_charts[x].append(None)
        


        # removing outliers
        denoised_charts = { x: [] for x in self.STEMS }
        
        for x in self.STEMS:
            previous = None
            for i in range(len(cleaned_charts[x])):

                if previous != None:
                    if cleaned_charts[x][i] != None:
                        previous = cleaned_charts[x][i]
                        if abs(cleaned_charts[x][i] - previous) > 10:
                            denoised_charts[x].append(None)
                            # dont add this value
                        else:  
                            denoised_charts[x].append(cleaned_charts[x][i])
                            # add this value
                    else:
                        denoised_charts[x].append(None)

                else:
                    if cleaned_charts[x][i] != None:
                        previous = cleaned_charts[x][i]
                    # never add first value
                    denoised_charts[x].append(None)




        # averaging out leftover values
        averaged_charts = { x: [] for x in self.STEMS }
        for x in self.STEMS:
            for i in range(1, len(denoised_charts[x])):
                if denoised_charts[x][i] != None and denoised_charts[x][i - 1] != None:
                    averaged_charts[x].append((denoised_charts[x][i] + denoised_charts[x][i - 1])/2)
                else:
                    if denoised_charts[x][i] != None:
                        averaged_charts[x].append(denoised_charts[x][i])
                    else:    
                        averaged_charts[x].append(None)

        # cutting off values that are too silent
        cut_charts = { x: [] for x in self.STEMS }
        for x in self.STEMS:
            for i in range(len(averaged_charts[x])):
                
                if averaged_charts[x][i] != None:
                    if averaged_charts[x][i] > -50:
                        cut_charts[x].append(averaged_charts[x][i])
                    else:
                        cut_charts[x].append(None)
                else:
                    cut_charts[x].append(None)

        # synthetising a diagnosis
        diagnosis = { x: [] for x in self.STEMS }
        for x in self.STEMS:
            ctr = 0
            for i in range(len(cut_charts[x])):
                
                if cut_charts[x][i] == None:
                    ctr += 1
                else:
                    ctr = 0

                if ctr == 0:
                    diagnosis[x].append(True) 
                elif ctr <= 7:
                    diagnosis[x].append(True)
                elif ctr > 7:
                    diagnosis[x].append(False)
                    diagnosis[x][-8:] = [False] * 8 

        if return_intermediate_steps == False:
            return diagnosis
        else:
            return [charts_dict, cleaned_charts, denoised_charts, averaged_charts, cut_charts, diagnosis]


    def analysing_pipeline(self):
        if self.track != "" and self.status != "Undefined":

            

            # calculate a simplified version of the waveform to display
            step_one = { x: [] for x in self.STEMS }

            for x in self.STEMS:
                # amt of values expected is 45
                for i in range(45):
                    d = self._raw_stems[x][ i *self.audio_len/45: (i+1)*self.audio_len/45 ]
                    silence_value = d.rms / d.max_possible_amplitude
                    step_one[x].append((round(silence_value*10000)/10000) ** 0.5)


            step_three = { x: [] for x in self.STEMS }
            # formatting stuff for prettier json
            for x in self.STEMS:  
                s = "0" if (self._raw_stems[x].rms/self._raw_stems[x].max_possible_amplitude)**0.5 < 0.1 else "1"
                step_three[x] = "|".join([s,";".join([str(i) for i in step_one[x]])])
            
            return step_three




if __name__ == "__main__":
    player = Player_obj(STEMS, SEPERATED_DIR)
    #vars


    
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
            player.analyse_audio(True)
        player.frame()