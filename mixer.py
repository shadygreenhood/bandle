#
# ||| OUTDATED |||
#


"""
stem_mixer_sync.py — Updated with searchable combobox

Features:
- Scans stems_final/<song> folders for .mp3 files
- Play / Pause (preserves position)
- Mute/unmute stems while keeping sync
- Reset Song button
- Visual progress bar
- Searchable song selector (live filtering)
"""

import os
import time
import ast
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
import csv
from pathlib import Path

import pygame

if "/" in str(Path(__file__)):
    PROJECT_DIR =  "/".join(str(Path(__file__).resolve().parent).split("/")[:-1])
elif "\\" in str(Path(__file__)):
    PROJECT_DIR =  "\\".join(str(Path(__file__).resolve().parent).split("\\")[:-1])
else:
    raise Exception(f"failed to resolve current project directory with cwd={str(Path(__file__))}")
SCRIPT_DIR = "bandle"
STEMS_FOLDER = PROJECT_DIR+"/"+"/separated/htdemucs_6s"
UPDATE_INTERVAL_MS = 100  # progress bar update interval
PLAYLIST_CSV = PROJECT_DIR+"/"+SCRIPT_DIR+"/playlist_CSV.txt"

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)


class StemMixer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stem Mixer (synced)")
        self.root.geometry("480x320")





        # State
        self.current_song = None
        self.stems = {}
        self.started = False
        self.playing = False
        self.start_time = 0.0
        self.paused_offset = 0.0
        self.total_length = 0.0
        self.songs = []
        self.playlist_IDs = []
        self.playlist_to_songs = {}
        self.playlist_to_names = {}

        # Load playlist data
        with open(PLAYLIST_CSV, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            headers = next(reader, [])
            headers = [h.strip() for h in headers]
            
            playlist_idx = 0
            friendly_name_idx = 1
            songs_idx = 2


            for row in reader:
                if len(row) > max(playlist_idx, songs_idx, friendly_name_idx):
                    playlist = row[playlist_idx].strip()
                    friendly_name = row[friendly_name_idx].strip()
                    if playlist and friendly_name:
                        if playlist not in self.playlist_to_names:
                            self.playlist_to_names[playlist] = friendly_name


                    playlist_songs = [s.replace(" ", "_") for s in ast.literal_eval(row[songs_idx].strip())]
                    if playlist and playlist_songs:
                        if playlist not in self.playlist_to_songs:
                            self.playlist_to_songs[playlist] = playlist_songs
   
        self.current_playlist = list(self.playlist_to_songs.keys())[0] if self.playlist_to_songs else None
        self.current_playlist_name = self.playlist_to_names.get(self.current_playlist, "") if self.current_playlist else ""

        self.songs = self.playlist_to_songs[self.current_playlist] if self.current_playlist in self.playlist_to_songs else []
        # Keep both lists but ensure we show names in the dropdown
        self.playlist_IDs = list(self.playlist_to_songs.keys())
        self.playlist_names = [self.playlist_to_names.get(pid, pid) for pid in self.playlist_IDs]

        self.current_song = self.songs[0] if self.songs else None

        # --- UI ---
        top_frame = ttk.Frame(root)
        top_frame.pack(pady=8, padx=8, fill="x")


        # --- Playlist Dropdown ---
        ttk.Label(top_frame, text="Playlist:").pack(side="left", padx=(0, 6))

        self.playlist_var = tk.StringVar(value=self.current_playlist_name)
        self.playlist_dropdown = ttk.Combobox(
            top_frame,
            textvariable=self.playlist_var,
            values=self.playlist_names,
            state="readonly",
            width=15
        )
        self.playlist_dropdown.pack(side="left", padx=(0, 12))
        self.playlist_dropdown.bind("<<ComboboxSelected>>", self.on_playlist_change)




        ttk.Label(top_frame, text="Select Song:").pack(side="left")

        # --- Search bar replacement for combobox ---
        self.song_var = tk.StringVar()
        self.song_var.set(self.current_song if self.current_song else "")
        
        self.search_entry = ttk.Entry(top_frame, textvariable=self.song_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))


        # Dropdown list (hidden until typing)
        self.listbox = tk.Listbox(root, height=5)
        self.listbox.place_forget()  # hide initially

        def update_listbox():
            """Update dropdown list as user types."""
            typed = self.song_var.get().strip().lower()
            matches = [s for s in self.songs if typed in s.lower()] if typed else self.songs

            self.listbox.delete(0, tk.END)
            for s in matches:
                self.listbox.insert(tk.END, s)

            if matches:
                # Position it under the search entry
                x = self.search_entry.winfo_rootx() - self.root.winfo_rootx()
                y = self.search_entry.winfo_rooty() - self.root.winfo_rooty() + self.search_entry.winfo_height()
                width = self.search_entry.winfo_width()
                self.listbox.place(x=x, y=y, width=width)
                self.listbox.lift()  # 👈 ensures it's above buttons/progress bar
            else:
                self.listbox.place_forget()

        def on_entry_key(event):
            update_listbox()
            if event.keysym == "Down" and self.listbox.size() > 0:
                self.listbox.focus_set()
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(0)
                self.listbox.activate(0)

        def on_listbox_key(event):
            if event.keysym == "Return":
                select_song()
            elif event.keysym == "Up" and self.listbox.curselection() == (0,):
                self.search_entry.focus_set()

        def select_song(event=None):
            """Triggered when selecting from list or pressing Enter."""
            selection = self.listbox.curselection()
            if selection:
                val = self.listbox.get(selection[0])
            else:
                val = self.song_var.get()

            if val in self.songs:
                self.song_var.set(val)
                self.load_song(val)
                self.listbox.place_forget()

        # Bindings
        self.search_entry.bind("<KeyRelease>", on_entry_key)
        self.search_entry.bind("<Return>", select_song)
        self.listbox.bind("<Return>", on_listbox_key)
        self.listbox.bind("<Double-Button-1>", select_song)
        self.listbox.bind("<Escape>", lambda e: self.listbox.place_forget())


        # --- Controls ---
        control_frame = ttk.Frame(root)
        control_frame.pack(padx=8, pady=(6, 12), fill="x")

        self.play_btn = ttk.Button(control_frame, text="Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=6)

        self.reset_btn = ttk.Button(control_frame, text="Reset Song", command=self.reset_song)
        self.reset_btn.pack(side="left", padx=6)

        # --- Progress bar ---
        progress_frame = ttk.Frame(root)
        progress_frame.pack(fill="x", padx=12)
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x")
        self.time_label = ttk.Label(progress_frame, text="00:00 / 00:00")
        self.time_label.pack(anchor="e")

        # --- Stem checkboxes ---
        self.stem_frame = ttk.LabelFrame(root, text="Stems")
        self.stem_frame.pack(fill="both", expand=True, padx=12, pady=(12, 8))

        if not self.songs:
            messagebox.showinfo(
                "No songs",
                f"No subfolders found in '{STEMS_FOLDER}'. Create one per song with 4 mp3 stems."
            )
        else:
            self.load_song(self.songs[0])

        # --- Updater ---
        self._updater_job = None
        self._schedule_update()

    def on_playlist_change(self, event=None):
        """Called when user selects a different playlist."""
        # Reverse lookup: find playlist ID by its friendly name
        selected_name = self.playlist_var.get()
        new_playlist = next((pid for pid, name in self.playlist_to_names.items() if name == selected_name), None)

        if new_playlist and new_playlist in self.playlist_to_songs:
            print("Old playlist:", self.current_playlist, "  Name:", self.current_playlist_name)
            self.current_playlist = new_playlist
            self.current_playlist_name = self.playlist_to_names.get(new_playlist, "")
            print("Switched to playlist:", new_playlist, "  Name:", self.current_playlist_name)
            self.songs = sorted(self.playlist_to_songs[new_playlist])
            self.listbox.delete(0, tk.END)
            self.listbox.place_forget()
            self.current_song = (self.songs[0])
            self.song_var.set(self.current_song)
            if self.current_song:
                self.load_song(self.current_song)

    def load_song(self, song_name):
        """Load stems for a song. Stops playback and resets internal state."""
        self._stop_all_channels()
        self.started = False
        self.playing = False
        self.paused_offset = 0.0
        self.start_time = 0.0
        self.total_length = 0.0
        self.progress["value"] = 0
        self.time_label.config(text="00:00 / 00:00")
        self.play_btn.config(text="Play")

        self.current_song = song_name
        song_path = os.path.join(STEMS_FOLDER, song_name)

        for w in self.stem_frame.winfo_children():
            w.destroy()
        self.stems.clear()

        files = sorted([f for f in os.listdir(song_path) if f.lower().endswith(".wav")])
        if not files:
            ttk.Label(self.stem_frame, text="No .mp3 stems found in this folder.").pack(padx=8, pady=8)
            return

        pygame.mixer.set_num_channels(max(len(files), pygame.mixer.get_num_channels(), 8))

        for idx, fname in enumerate(files):
            path = os.path.join(song_path, fname)
            name = os.path.splitext(fname)[0]

            try:
                sound = pygame.mixer.Sound(path)
            except Exception as e:
                ttk.Label(self.stem_frame, text=f"Error loading {fname}: {e}").pack(anchor="w")
                continue

            ch = pygame.mixer.Channel(idx)
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                self.stem_frame, text=name, variable=var, command=lambda n=name: self._on_toggle(n)
            )
            cb.pack(anchor="w", padx=6, pady=2)

            self.stems[name] = {"sound": sound, "channel": ch, "var": var}
            self.total_length = max(self.total_length, sound.get_length())

        self._update_time_label(0.0, self.total_length)

    def toggle_play(self):
        """Toggle play/pause."""
        if not self.started:
            self._start_all()
        elif not self.playing:
            self._resume_all()
        else:
            self._pause_all()

    def _start_all(self):
        for name, s in self.stems.items():
            vol = 1.0 if s["var"].get() else 0.0
            s["channel"].set_volume(vol)
            s["channel"].play(s["sound"], loops=0)
        self.started = True
        self.playing = True
        self.start_time = time.time() - self.paused_offset
        self.play_btn.config(text="Pause")

    def _resume_all(self):
        for s in self.stems.values():
            s["channel"].unpause()
        self.playing = True
        self.start_time = time.time() - self.paused_offset
        self.play_btn.config(text="Pause")

    def _pause_all(self):
        for s in self.stems.values():
            s["channel"].pause()
        self.paused_offset = time.time() - self.start_time
        self.playing = False
        self.play_btn.config(text="Play")

    def reset_song(self):
        self._stop_all_channels()
        self.started = False
        self.playing = False
        self.paused_offset = 0.0
        self.start_time = 0.0
        self.progress["value"] = 0
        self._update_time_label(0.0, self.total_length)
        self.play_btn.config(text="Play")

    def _stop_all_channels(self):
        for s in self.stems.values():
            s["channel"].stop()

    def _on_toggle(self, name):
        s = self.stems.get(name)
        if not s:
            return
        enabled = s["var"].get()
        s["channel"].set_volume(1.0 if enabled else 0.0)

    def _schedule_update(self):
        if self._updater_job:
            self.root.after_cancel(self._updater_job)
        self._updater_job = self.root.after(UPDATE_INTERVAL_MS, self._update_progress)

    def _update_progress(self):
        if self.playing:
            elapsed = time.time() - self.start_time
        else:
            elapsed = self.paused_offset

        elapsed = max(0.0, elapsed)
        total = max(0.0001, self.total_length)
        percent = min(100.0, (elapsed / total) * 100.0)
        self.progress["value"] = percent
        self._update_time_label(elapsed, total)

        if elapsed >= total and self.started and self.playing:
            for s in self.stems.values():
                s["channel"].stop()
            self.playing = False
            self.paused_offset = total
            self.play_btn.config(text="Play")

        self._schedule_update()

    def _update_time_label(self, elapsed, total):
        def fmt(s):
            s = int(round(s))
            m = s // 60
            sec = s % 60
            return f"{m:02d}:{sec:02d}"

        self.time_label.config(text=f"{fmt(elapsed)} / {fmt(total)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StemMixer(root)
    root.mainloop()

