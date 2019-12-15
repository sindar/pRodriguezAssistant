# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import psutil
import os.path
import time
from threading import Timer

class MusicPlayer:

    def __init__(self):
        self.playing_timer = None
        self.tracks_count = 0
        self.next_track = 0
        self.musicIsPlaying = False
        self.music_dir = '/home/pi/music/'
        self.playlist = self.read_playlist(self.music_dir + 'playlist')

    def read_playlist(self, filename):
        playlist = []
        if os.path.isfile(filename):
            with open(filename) as fp:
                line = fp.readline()
                self.tracks_count = 1
                playlist.append(line)
                while line:
                    line = fp.readline()
                    playlist.append(line)
                    self.tracks_count += 1
        else:
            print('Error ' + filename + ' does not exist')
        return playlist

    def send_command(self, command):
        play_pids = [process.pid for process in psutil.process_iter() if 'play' in str(process.name) and 'music'
                     in str(process.cmdline())]
        if command == 'start':
            if len(play_pids) > 0:
                self.kill_player()

            if(self.playlist):
                self.musicIsPlaying = True
                self.play_next_track()
                if self.playing_timer:
                    self.playing_timer.cancel()
                    self.playing_timer = None
                self.playing_timer = Timer(5.0, self.check_playing_ended)
                self.playing_timer.start()
        elif command == 'stop':
            if len(play_pids) > 0:
                self.kill_player()
                self.musicIsPlaying = False
        elif command == 'pause':
            if len(play_pids) > 0:
                stop_exe = 'kill -STOP ' + str(play_pids[0])
                p = subprocess.Popen(["%s" % stop_exe], shell=True, stdout=subprocess.PIPE)
        elif command == 'resume':
            if len(play_pids) > 0:
                cont_exe = 'kill -CONT ' + str(play_pids[0])
                p = subprocess.Popen(["%s" % cont_exe], shell=True, stdout=subprocess.PIPE)
            else:
                self.play_next_track()
            self.musicIsPlaying = True
        elif command == 'next':
            if len(play_pids) > 0:
                self.kill_player()
            self.musicIsPlaying = True
            self.play_next_track()
        elif command == 'status':
            if len(play_pids) < 1:
                self.musicIsPlaying = False
            else:
                self.musicIsPlaying = True
        elif command == 'exit':
            self.playing_timer.cancel()
            self.playing_timer = None
            self.musicIsPlaying = False
            self.kill_player()

    def check_playing_ended(self):
        if self.playing_timer:
            self.playing_timer.cancel()
            self.playing_timer = None

        if self.musicIsPlaying:
            play_pids = [process.pid for process in psutil.process_iter() if
                         'play' in str(process.name) and 'music' in str(process.cmdline())]
            if len(play_pids) < 1:
                self.play_next_track()
            self.playing_timer = Timer(5.0, self.check_playing_ended)
            self.playing_timer.start()

    def play_next_track(self):
        current_milli_time = int(round(time.time() * 1000))
        self.next_track = current_milli_time % self.tracks_count
        play_exe = 'play ' + '"' + self.music_dir + str(self.playlist[self.next_track]).rstrip('\n') + '"'
        player = subprocess.Popen(["%s" % play_exe], shell=True, stdout=subprocess.PIPE)

    def kill_player(self):
        kill_exe = 'killall -s SIGKILL play'
        p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()