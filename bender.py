# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
from threading import Timer
import psutil

fsmState = 1
isSleeping = False
musicIsPlaying = False

def main():
    global fsmState
    global eyes_on
    global eyes_off
    global teeth_on
    global teeth_off
    global backlightEnabled
    global micGain

    kill_pocketsphinx()
    kill_player()

    backlight(teeth_off)
    backlight(eyes_off)
    time.sleep(0.15)
    backlight(eyes_on)

    mic_set(micGain)

    ps = PsLiveRecognizer('./resources/', 'bender')
    p = subprocess.Popen(["%s" % ps.cmd_line], shell=True, stdout=subprocess.PIPE)

    print(["%s" % ps.cmd_line])

    while True:
        if (fsmState == 1):
            if find_keyphrase(p):
                conversation_mode(p)
            #elif (fsmState == 2):
            #    configuration_mode(p)
        elif (fsmState == 4):
            break
        else:
            continue

    kill_pocketsphinx()
    backlight(eyes_off)

def sleep_timeout():
    global isSleeping
    play_answer('kill all humans')
    isSleeping = True

def find_keyphrase(p):
    global fsmState
    global sleepEnabled
    global musicIsPlaying

    while True:
        keyphrase_found = False
        print('Start mode:')

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if PsLiveRecognizer.lang == 'ru':
            try:
                utt = tr_start_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if ('bender' in utt):
            music('status')
            if musicIsPlaying:
                if('stop' in utt):
                    music('pause')
                    keyphrase_found = True
            else:
                if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
                    command = 'hey bender ' + str(current_milli_time % 3)
                    play_answer(command)
                keyphrase_found = True

        time.sleep(0.15)
        if keyphrase_found:
            backlight(teeth_on_ok)
            return keyphrase_found

def conversation_mode(p):
    global fsmState
    global sleepEnabled
    global isSleeping

    while True:
        print ('Conversation mode:')
        sleepTimer = None

        if sleepEnabled:
            sleepTimer = Timer(SLEEPING_TIME, sleep_timeout)
            sleepTimer.start()

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if PsLiveRecognizer.lang == 'ru':
            try:
                utt = tr_conversation_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if sleepEnabled:
            if utt != None and sleepTimer != None:
                sleepTimer.cancel()
            if utt != None and isSleeping:
                utt = 'wake up'
                isSleeping = False

        if 'shutdown' in utt:
            command = 'shutdown'
            fsmState = 4
        #elif ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
        #    command = 'exit'
        #    fsmState = 0
        elif ('sing' in utt) or ('song' in utt):
            command = 'sing'
        elif 'who are you' in utt:
            command = 'who are you ' + str(current_milli_time % 2)
        elif 'how are you' in utt:
            command = 'how are you'
        elif ('where are you from' in utt) or ('where were you born' in utt):
            command = 'birthplace'
        elif 'when were you born' in utt:
            command = 'birthdate'
        elif 'your favorite animal' in utt:
            command = 'animal'
        elif ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
            command = 'hey bender ' + str(current_milli_time % 3)
        elif 'magnet' in utt:
            command = 'magnet ' + str(current_milli_time % 2)
        elif 'new sweater' in utt:
            command = 'new sweater'
        elif ('wake up' in utt) or ('awake' in utt):
            command = 'wake up'
        elif ('configuration' in utt) or ('configure' in utt):
            command = 'configuration'
            #fsmState = 2
        elif ('enable music player' in utt):
            command = 'no audio'
            music('start')
            time.sleep(1)
        elif ('disable music player' in utt):
            command = 'no audio'
            music('stop')
        else:
            command = 'unrecognized'

        if command != 'no audio':
            play_answer(command)
        else:
            backlight(teeth_off)

        music('status')
        if musicIsPlaying:
            music('resume')

        time.sleep(0.15)
        break

def music(command):
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

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def kill_player():
    kill_exe = 'killall -s SIGKILL play'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def configuration_mode(p):
    global fsmState

    while True:
        print('Configuration mode:')

        if sleepEnabled:
            sleepTimer = Timer(SLEEPING_TIME, sleep_timeout)
            sleepTimer.start()

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if PsLiveRecognizer.lang == 'ru':
            try:
                utt = tr_configuration_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if sleepEnabled:
            if utt != None and sleepTimer != None:
                sleepTimer.cancel()
            if utt != None and isSleeping:
                utt = 'wake up'
                isSleeping = False

        if ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
            command = 'hey bender ' + str(current_milli_time % 3)
            play_answer(command)
            fsmState = 1
        if ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
            command = 'exit'
            #fsmState = 0
        elif ('set' in utt):
            command = 'set'
            #TODO: implement set logic
        elif('enable' in utt):
            command = 'enable'
            #TODO: implement enable logic
        elif('disable' in utt):
            command = 'disable'
            #TODO: implement disable logic
        else:
            command = 'unrecognized'

        play_answer(command)
        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 2):
            break

main()
