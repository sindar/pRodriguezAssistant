# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import psutil

def music_player(command):
    global musicIsPlaying

    play_pids = [process.pid for process in psutil.process_iter() if 'play' in str(process.name) and 'music' in str(process.cmdline())]
    if command == 'start':
        if len(play_pids) > 0:
            kill_player()

        play_exe = 'play /home/pi/music/1.mp3'
        player = subprocess.Popen(["%s" % play_exe], shell=True, stdout=subprocess.PIPE)
        musicIsPlaying = True
    elif command == 'stop':
        if len(play_pids) > 0:
            kill_player()
            musicIsPlaying = False
    elif command == 'pause':
        if len(play_pids) > 0:
            stop_exe = 'kill -STOP ' + str(play_pids[0])
            p = subprocess.Popen(["%s" % stop_exe], shell=True, stdout=subprocess.PIPE)
    elif command == 'resume':
        if len(play_pids) > 0:
            cont_exe = 'kill -CONT ' + str(play_pids[0])
            p = subprocess.Popen(["%s" % cont_exe], shell=True, stdout=subprocess.PIPE)
            musicIsPlaying = True
    elif command == 'status':
        if len(play_pids) < 1:
            musicIsPlaying = False

def kill_player():
    kill_exe = 'killall -s SIGKILL play'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()