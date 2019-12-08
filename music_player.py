# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import psutil
import os.path

class MusicPlayer:

    def __init__(self, filename):
        self.current_track = 0
        self.musicIsPlaying = False
        self.playlist = self.read_playlist(filename)

    def __del__(self):
        if self.playlist != None:
            self.playlist.close()

    def read_playlist(self, filename):
        playlist = None
        if os.path.isfile(filename):
            playlist = open(filename, "r")
            try:
                self.tracks_count = int(playlist.readline())
            except TypeError as e:
                print('Number of tracks is not numeric!')
                self.tracks_count = 0
                playlist = None
        else:
            print('Error ' + filename + ' does not exist')
        return playlist

    def send_command(self, command):
        play_pids = [process.pid for process in psutil.process_iter() if 'play' in str(process.name) and 'music' in str(process.cmdline())]
        if command == 'start':
            if len(play_pids) > 0:
                kill_player()

            play_exe = 'play /home/pi/music/1.mp3'
            player = subprocess.Popen(["%s" % play_exe], shell=True, stdout=subprocess.PIPE)
            self.musicIsPlaying = True
        elif command == 'stop':
            if len(play_pids) > 0:
                kill_player()
                self.musicIsPlaying = False
        elif command == 'pause':
            if len(play_pids) > 0:
                stop_exe = 'kill -STOP ' + str(play_pids[0])
                p = subprocess.Popen(["%s" % stop_exe], shell=True, stdout=subprocess.PIPE)
        elif command == 'resume':
            if len(play_pids) > 0:
                cont_exe = 'kill -CONT ' + str(play_pids[0])
                p = subprocess.Popen(["%s" % cont_exe], shell=True, stdout=subprocess.PIPE)
                self.musicIsPlaying = True
        elif command == 'status':
            if len(play_pids) < 1:
                self.musicIsPlaying = False
            else:
                self.musicIsPlaying = True

    def kill_player(self):
        kill_exe = 'killall -s SIGKILL play'
        p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()