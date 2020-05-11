# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess

class MusicPlayer:

    def __init__(self):
        self.musicIsPlaying = False

    def __mpc_command(self, command):
        p = subprocess.Popen(["%s" % 'mpc ' + command], shell=True, stdout=subprocess.PIPE)

    def send_command(self, command):
        if command == 'start':
            self.__mpc_command('play')
            self.musicIsPlaying = True
        elif command == 'stop':
            self.__mpc_command('stop')
            self.musicIsPlaying = False
        elif command == 'pause':
            self.__mpc_command('pause')
        elif command == 'resume':
            self.__mpc_command('play')
            self.musicIsPlaying = True
        elif command == 'next':
            self.__mpc_command('next')
            self.musicIsPlaying = True