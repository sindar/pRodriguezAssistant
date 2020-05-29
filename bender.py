# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import threading
import sys
from speech_recognizer import PsLiveRecognizer
from answer_player import AnswerPlayer
from music_player import MusicPlayer
from backlight_control import BacklightControl
from translation_ru import TranslatorRU
import ups_lite
import power
import volume_control

audio_lang = 'en'
recognize_lang ='en'

BacklightControl.backlight_enabled = True
eyes_bl = BacklightControl('EYES')

fsm_state = 1

m_player = MusicPlayer()
a_player = AnswerPlayer(audio_lang)
speech_recognizer = PsLiveRecognizer('./resources/', recognize_lang, 'bender')

IDLE_TIME = 60 # in minutes, 2 - minimum
sleep_enabled = True
is_sleeping = False
sleep_counter = 0
sleep_counter_lock = threading.Lock()
main_thread_is_running = True

UPS_TASK_ENABLED = True
UPS_TASK_INTERVAL = 2

def main():
    global fsm_state
    global m_player
    global speech_recognizer
    global main_thread_is_running

    volume_control.set_speaker_volume(volume_control.speaker_volume)

    kill_pocketsphinx()
    m_player.send_command('stop')

    eyes_bl.exec_cmd('OFF')
    time.sleep(0.15)

    if UPS_TASK_ENABLED:
        ups_thread = threading.Thread(target=ups_task)
        ups_thread.start()

    sleep_thread = threading.Thread(target=sleep_task)
    sleep_thread.daemon = True
    sleep_thread.start()

    sphinx_proc = subprocess.Popen(["%s" % speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % speech_recognizer.cmd_line])

    eyes_bl.exec_cmd('ON')

    while True:
        if (fsm_state == 1):
            if find_keyphrase(sphinx_proc):
                conversation_mode(sphinx_proc)
        elif (fsm_state == 2):
            conversation_mode(sphinx_proc)
        elif (fsm_state == 3):
            break
        elif (fsm_state == 4):
            break
        elif (fsm_state == 5):
            break
        else:
            continue

    main_thread_is_running = False
    kill_pocketsphinx()
    m_player.send_command('stop')

    eyes_bl.exec_cmd('OFF')
    time.sleep(3)
    
    if (fsm_state == 4):
        power.shutdown()

    if (fsm_state == 5):
        power.reboot()

    sys.exit(0)

def ups_task():
    global main_thread_is_running
    prev_voltage = ups_lite.read_voltage()
    prev_capacity = ups_lite.read_capacity()
    while main_thread_is_running:
        time.sleep(UPS_TASK_INTERVAL)
        voltage = ups_lite.read_voltage()
        capacity = ups_lite.read_capacity()
        if voltage >= 4.20:
            if prev_voltage <= 4.15:
                a_player.play_answer('electricity')
        else:
            if capacity < 20 and (prev_capacity > capacity):
                power.shutdown()
        prev_voltage = voltage
        prev_capacity = capacity

def sleep_task():
    global is_sleeping
    global sleep_enabled
    global sleep_counter

    while main_thread_is_running:
        time.sleep(60)
        if sleep_enabled:
            sleep_counter_inc()
            if sleep_counter >= IDLE_TIME:
                if not is_sleeping:
                    if not m_player.musicIsPlaying:
                        eyes_bl.exec_cmd('OFF')
                        a_player.play_answer('kill all humans')
                        is_sleeping = True

def sleep_counter_inc():
    global sleep_counter
    sleep_counter_lock.acquire()
    sleep_counter += 1
    sleep_counter_lock.release()

def sleep_counter_reset():
    global sleep_counter
    sleep_counter_lock.acquire()
    sleep_counter = 0
    sleep_counter_lock.release()

def wake_up():
    global is_sleeping
    eyes_bl.exec_cmd('ON')
    answer = 'wake up'
    a_player.play_answer(answer)
    is_sleeping = False

def get_utterance(sphinx_proc):
    retcode = sphinx_proc.returncode
    utt = sphinx_proc.stdout.readline().decode('utf8').rstrip().lower()
    print('utterance = ' + utt)
    return utt

def find_keyphrase(sphinx_proc):
    global fsm_state
    global sleep_enabled
    global is_sleeping
    global aplayer

    while True:
        keyphrase_found = False
        print('Start mode:')

        utt = get_utterance(sphinx_proc)

        if speech_recognizer.lang == 'ru':
            try:
                utt = TranslatorRU.tr_start_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if ('bender' in utt):
            sleep_counter_reset()
            if m_player.musicIsPlaying:
                if('pause' in utt or 'stop' in utt or volume_control.speaker_volume == 0):
                    m_player.send_command('pause')
                    keyphrase_found = True
            else:
                if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)) and not is_sleeping:
                    answer = 'hey bender'
                    a_player.play_answer(answer)
                if is_sleeping:
                    wake_up()
                keyphrase_found = True

        if keyphrase_found:
            return keyphrase_found

def conversation_mode(sphinx_proc):
    global fsm_state
    global sleep_enabled
    global is_sleeping
    global a_player

    while True:
        fsm_state = 1
        print ('Conversation mode:')

        utt = get_utterance(sphinx_proc)

        if speech_recognizer.lang == 'ru':
            try:
                utt = TranslatorRU.tr_conversation_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if is_sleeping:
            wake_up()
        else:
            before_action = None
            before_parameter = None
            after_action = None
            after_parameter = None
            answer = 'unrecognized'
            if 'shutdown' in utt:
                answer = 'shutdown'
                fsm_state = 4
            if 'reboot' in utt:
                answer = 'reboot'
                fsm_state = 5
            elif (('exit' in utt) or ('quit' in utt)) and ('program' in utt):
                answer = 'exit'
                fsm_state = 3
            elif (utt.endswith('mode')):
                if utt.startswith('quiet') or utt.startswith('normal') or utt.startswith('loud'):
                    (mode, *_) = utt.split(maxsplit=1)
                    before_action = volume_control.set_speaker_volume
                    before_parameter = volume_control.volume_modes[mode]
                    answer = 'configuration'
            elif ('volume' in utt) or (utt == 'louder') or (utt == 'quieter'):
                answer = 'configuration'
                if ('increase' in utt or utt == 'louder'):
                    before_action = volume_control.change_speaker_volume
                    before_parameter = volume_control.VOLUME_STEP
                elif ('decrease' in utt or utt == 'quieter'):
                    before_action = volume_control.change_speaker_volume
                    before_parameter = -volume_control.VOLUME_STEP
            elif ('sing' in utt) and ('song' in utt):
                answer = 'sing'
            elif 'who are you' in utt:
                answer = 'who are you'
            elif 'how are you' in utt:
                answer = 'how are you'
            elif ('where are you from' in utt) or ('where were you born' in utt):
                answer = 'birthplace'
            elif 'when were you born' in utt:
                answer = 'birthdate'
            elif 'your favorite animal' in utt:
                answer = 'animal'
            elif 'how can you live' in utt and 'without' in utt and 'body' in utt:
                answer = 'body'
            elif 'what do you think about' in utt:
                if 'alexa' in utt or 'alice' in utt or 'cortana' in utt or 'siri' in utt:
                    answer = 'bad girl'
            elif 'magnet' in utt:
                answer = 'magnet'
            elif 'new sweater' in utt:
                answer = 'new sweater'
            elif ('start' in utt and 'player' in utt):
                answer = 'player'
                after_action = m_player.send_command
                after_parameter = 'start'
            elif ('stop' in utt and 'player' in utt):
                answer = 'player'
                after_action = m_player.send_command
                after_parameter = 'stop'
            elif (utt == 'next song' or utt == 'next track'):
                answer = 'no audio'
                after_action = m_player.send_command
                after_parameter = 'next'
            elif ('enable' in utt):
                if ('sleep' in utt):
                    answer = 'configuration'
                    sleep_enabled = True
            elif ('disable' in utt):
                if ('sleep' in utt):
                    answer = 'configuration'
                    sleep_enabled = False
            elif (utt == 'bender' or ('bender' in utt and ('hi' in utt or 'pause' in utt))):
                answer = 'no audio'
                fsm_state = 2

            print ("answer = " + answer)

            if fsm_state != 2:
                run_action(before_action, before_parameter)

                if answer != 'no audio':
                    a_player.play_answer(answer)

                run_action(after_action, after_parameter)

                if answer != 'shutdown' or answer != 'reboot':
                    if m_player.musicIsPlaying:
                        m_player.send_command('resume')
        sleep_counter_reset()

        break

def run_action(action, parameter):
    if action:
        if parameter:
            action(parameter)
        else:
            action()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
