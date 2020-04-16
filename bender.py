# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
from threading import Timer
from multiprocessing import Process
from speech_recognizer import PsLiveRecognizer
from answer_player import AnswerPlayer
from music_player import MusicPlayer
from backlight_control import BacklightControl
from translation_ru import TranslatorRU
import ups_lite

audio_lang = 'en'
recognize_lang ='en'
sleepEnabled = True

BacklightControl.backlight_enabled = True
eyes_bl = BacklightControl('EYES')

fsmState = 1
isSleeping = False
m_player = MusicPlayer()
a_player = AnswerPlayer(audio_lang)
speech_recognizer = PsLiveRecognizer('./resources/', recognize_lang, 'bender')

speaker_volume = 10

SLEEPING_TIME = 600.0
BACKGROUND_TASKS_INTERVAL = 1
VOLUME_STEP = 4

def main():
    global fsmState
    global m_player
    global speech_recognizer
    global speaker_volume

    set_speaker_volume(speaker_volume)

    kill_pocketsphinx()
    m_player.kill_player()

    eyes_bl.exec_cmd('OFF')
    time.sleep(0.15)

    background_proc = Process(target=background_tasks, args=())
    background_proc.start()

    p = subprocess.Popen(["%s" % speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % speech_recognizer.cmd_line])

    eyes_bl.exec_cmd('ON')

    while True:
        if (fsmState == 1):
            if find_keyphrase(p):
                conversation_mode(p)
        elif (fsmState == 2):
            conversation_mode(p)
        elif (fsmState == 3):
            break
        elif (fsmState == 4):
            break
        else:
            continue

    kill_pocketsphinx()
    m_player.send_command("exit")

    eyes_bl.exec_cmd('OFF')
    if background_proc != None:
        background_proc.terminate()
    time.sleep(3)
    
    if (fsmState == 4):
        shutdown()

def background_tasks():
    power_plugged = True
    prev_voltage = ups_lite.read_voltage()
    prev_capacity = ups_lite.read_capacity()
    while True:
        voltage = ups_lite.read_voltage()
        capacity = ups_lite.read_capacity()
        if voltage < prev_voltage or capacity < prev_capacity:
            if power_plugged:
                power_plugged = False
        if voltage > prev_voltage or capacity > prev_capacity:
            if not power_plugged:
                power_plugged = True
                a_player.play_answer('electricity')
        # if sleepEnabled:
        #     sleepTimer = Timer(SLEEPING_TIME, sleep_timeout)
        #     sleepTimer.start()
        time.sleep(BACKGROUND_TASKS_INTERVAL)

def sleep_timeout():
    global isSleeping
    global a_player
    a_player.play_answer('kill all humans')
    isSleeping = True

def find_keyphrase(p):
    global fsmState
    global sleepEnabled
    global aplayer
    global speaker_volume

    while True:
        keyphrase_found = False
        print('Start mode:')

        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if speech_recognizer.lang == 'ru':
            try:
                utt = TranslatorRU.tr_start_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if ('bender' in utt):
            m_player.send_command('status')
            if m_player.musicIsPlaying:
                if('pause' in utt or speaker_volume == 0):
                    m_player.send_command('pause')
                    keyphrase_found = True
            else:
                # if sleepEnabled:
                #     if utt != None and sleepTimer != None:
                #         sleepTimer.cancel()
                #     if utt != None and isSleeping:
                #         utt = 'wake up'
                #         isSleeping = False
                if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
                    command = 'hey bender'
                    a_player.play_answer(command)
                keyphrase_found = True

        if keyphrase_found:
            return keyphrase_found

def conversation_mode(p):
    global fsmState
    global sleepEnabled
    global isSleeping
    global a_player

    while True:
        fsmState = 1
        print ('Conversation mode:')

        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if speech_recognizer.lang == 'ru':
            try:
                utt = TranslatorRU.tr_conversation_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if 'shutdown' in utt:
            command = 'shutdown'
            fsmState = 4
        elif (('exit' in utt) or ('quit' in utt)) and ('program' in utt):
            command = 'exit'
            fsmState = 3
        elif ('volume' in utt):
            command = 'no audio'
            if ('increase' in utt):
                change_speaker_volume(VOLUME_STEP)
            elif ('decrease' in utt):
                change_speaker_volume(-VOLUME_STEP)
        elif ('sing' in utt) and ('song' in utt):
            command = 'sing'
        elif 'who are you' in utt:
            command = 'who are you'
        elif 'how are you' in utt:
            command = 'how are you'
        elif ('where are you from' in utt) or ('where were you born' in utt):
            command = 'birthplace'
        elif 'when were you born' in utt:
            command = 'birthdate'
        elif 'your favorite animal' in utt:
            command = 'animal'
        elif 'how can you live' in utt and 'without' in utt and 'body' in utt:
            command = 'body'
        elif 'what do you think about' in utt:
            if 'alexa' in utt or 'alice' in utt or 'cortana' in utt or 'siri' in utt:
                command = 'bad girl'
        elif 'magnet' in utt:
            command = 'magnet'
        elif 'new sweater' in utt:
            command = 'new sweater'
        elif ('wake up' in utt) or ('awake' in utt):
            command = 'wake up'
        elif ('start' in utt and 'player' in utt):
            command = 'player'
            m_player.send_command('start')
            time.sleep(1)
        elif ('stop' in utt and 'player' in utt):
            command = 'player'
            m_player.send_command('stop')
        elif ('next song' in utt):
            command = 'no audio'
            m_player.send_command('next')
        elif ('enable' in utt):
            if ('sleep' in utt):
                command = 'configuration'
                sleepEnabled = True
            else:
                command = 'unrecognized'
        elif ('disable' in utt):
            if ('sleep' in utt):
                command = 'configuration'
                sleepEnabled = False
            else:
                command = 'unrecognized'
        elif (utt == 'bender' or ('bender' in utt and ('hi' in utt or 'pause' in utt))):
            command = 'no audio'
            fsmState = 2
        else:
            command = 'unrecognized'

        if fsmState != 2:
            if command != 'no audio':
                a_player.play_answer(command)

            if command != 'shutdown':
                m_player.send_command('status')
                if m_player.musicIsPlaying:
                    m_player.send_command('resume')

        break

def change_speaker_volume(value):
    global speaker_volume

    speaker_volume += value
    if speaker_volume < 0:
        speaker_volume = 0
    if speaker_volume > 40:
        speaker_volume = 40
    set_speaker_volume(speaker_volume)

def set_speaker_volume(value):
    amixer_exe = "amixer -q -c 1 sset 'Speaker' " + str(value)
    p = subprocess.Popen(["%s" % amixer_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def shutdown():
    shutdown = "shutdown -Ph now"
    p = subprocess.Popen(["%s" % shutdown], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
