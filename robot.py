#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import threading
import sys
import getopt
import pathlib
import psutil
from common import power
from common.speech_recognizer import PsLiveRecognizer
from profiles.bender import bender as profile

main_thread_is_running = True

SLEEP_TASK_ENABLED = profile.SLEEP_TASK_ENABLED
IDLE_TIME = 60 # in minutes, 2 - minimum
sleep_enabled = False
is_sleeping = False
sleep_counter = 0
sleep_counter_lock = threading.Lock()

UPS_TASK_ENABLED = profile.UPS_TASK_ENABLED
UPS_TASK_INTERVAL = 2
if UPS_TASK_ENABLED: from common import ups_lite

fsm_state = 1
fsm_transition = {
    'repeated keyphrase': 2,
    'exit': 3,
    'reboot': 4,
    'shutdown': 5,
    'rss start': 6,
    'rss end': 1
}

speech_recognizer = None

def sleep_enable_set(val):
    global sleep_enabled
    sleep_enabled = val

def main(argv):
    global main_thread_is_running
    global fsm_state
    global sleep_enabled
    global speech_recognizer

    profile.vol_ctrl.set_speaker_volume(profile.vol_ctrl.speaker_volume)

    kill_pocketsphinx()
    profile.m_player.send_command('stop')

    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('OFF')
    time.sleep(0.15)

    if UPS_TASK_ENABLED:
        ups_thread = threading.Thread(target=ups_task)
        ups_thread.start()

    if SLEEP_TASK_ENABLED:
        sleep_enabled = True
        profile.sleep_enable_set = sleep_enable_set
        sleep_thread = threading.Thread(target=sleep_task)
        sleep_thread.daemon = True
        sleep_thread.start()

    speech_recognizer = PsLiveRecognizer(str(pathlib.Path().absolute()) + '/common/resources/',
                                         str(pathlib.Path().absolute()) + '/profiles/' + profile.name + '/resources/',
                                         profile.recognize_lang, profile.name)
    sphinx_proc = subprocess.Popen(["%s" % speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % speech_recognizer.cmd_line])
   
    time.sleep(10)

    expected_sphinx_pid = sphinx_proc.pid + 1
    if psutil.pid_exists(expected_sphinx_pid) == True:
        sphinx_pids = [process.pid for process in psutil.process_iter() if 'pocketsphinx_co' in str(process.name)]
        if sphinx_pids == None:
            print('No pocketsphinx_continuous processes!')
            sys.exit(1)
        if len(sphinx_pids) > 1:
            print('More than one pocketsphinx_continuous processes!')
            sys.exit(1)
        if len(sphinx_pids) == 1 and (expected_sphinx_pid in sphinx_pids):
            print('pocketsphinx_continuous successfully started')
    else:
        print('Error while starting pocketsphinx_continuous!')
        sys.exit(1)

    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('ON')

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
        elif (fsm_state == 6):
            rss_read_mode(sphinx_proc)
        else:
            continue

    main_thread_is_running = False
    kill_pocketsphinx()
    profile.m_player.send_command('stop')

    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('OFF')
    time.sleep(3)

    if (fsm_state == 4):
        power.reboot()

    if (fsm_state == 5):
        power.shutdown()

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
                profile.a_player.play_answer('electricity')
        else:
            if capacity < 20 and (prev_capacity > capacity):
                power.shutdown()
        prev_voltage = voltage
        prev_capacity = capacity

def sleep_task():
    global is_sleeping
    global sleep_enabled
    global sleep_counter
    global speech_recognizer

    while main_thread_is_running:
        time.sleep(60)
        if sleep_enabled:
            sleep_counter_inc()
            if sleep_counter >= IDLE_TIME:
                if not is_sleeping:
                    if not profile.m_player.musicIsPlaying:
                        if profile.eyes_bl:
                            profile.eyes_bl.exec_cmd('OFF')
                        profile.a_player.play_answer('fall asleep')
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
    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('ON')
    profile.a_player.play_answer('wake up')
    is_sleeping = False

def get_utterance(sphinx_proc):
    retcode = sphinx_proc.returncode
    utt = sphinx_proc.stdout.readline().decode('utf8').rstrip().lower()
    print('utterance = ' + utt)
    return utt

def find_keyphrase(sphinx_proc):
    global sleep_enabled
    global is_sleeping
    global aplayer
    global fsm_state

    keyphrase_found = False
    print('Start mode:')

    utt = get_utterance(sphinx_proc)

    if speech_recognizer.lang == 'ru':
        try:
            utt = profile.STTTranslatorRU.tr_start_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

    if (profile.name in utt):
        if sleep_enabled:
            sleep_counter_reset()
        if profile.m_player.musicIsPlaying:
            if('pause' in utt or 'stop' in utt or profile.vol_ctrl.speaker_volume == 0):
                profile.m_player.send_command('pause')
                keyphrase_found = True
        else:
            if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)) and not is_sleeping:
                answer = 'hey ' + profile.name
                profile.a_player.play_answer(answer)
            if is_sleeping:
                wake_up()
            keyphrase_found = True

    return keyphrase_found

def conversation_mode(sphinx_proc):
    global sleep_enabled
    global is_sleeping
    global fsm_state
    global speech_recognizer

    print ('Conversation mode:')

    utt = get_utterance(sphinx_proc)

    if speech_recognizer.lang == 'ru':
        try:
            utt = profile.STTTranslatorRU.tr_conversation_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

    if is_sleeping:
        wake_up()
    else:
        before_action = None
        after_action = None

        try:
            action = profile.actions[utt]
            answer = action[0]
            before_action = action[1]
            after_action = action[2]
        except KeyError as e:
            answer = 'unrecognized'

        print ("answer = " + answer)

        try:
            fsm_state = fsm_transition[answer]
        except:
            fsm_state = 1

        confirmation_needed = None

        if before_action:
            confirmation_needed = before_action()

        if confirmation_needed:
            profile.a_player.play_answer('confirmation')
            if not get_confirmation(sphinx_proc):
                answer = 'no audio'
                after_action = None
            else:
                answer = 'confirmed'

        if answer != 'no audio' and answer != 'rss next' and answer != 'rss next':
            profile.a_player.play_answer(answer)

        if after_action:
            after_action()

        if answer != 'shutdown' or answer != 'reboot':
            if profile.m_player.musicIsPlaying:
                profile.m_player.send_command('resume')

    if sleep_enabled:
        sleep_counter_reset()

def rss_read_mode(sphinx_proc):
    global sleep_enabled
    global is_sleeping
    global fsm_state
    global speech_recognizer

    print ('RSS reader mode:')

    utt = get_utterance(sphinx_proc)

    if speech_recognizer.lang == 'ru':
        try:
            utt = profile.STTTranslatorRU.tr_conversation_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))
    
    if (profile.name in utt):
        if sleep_enabled:
            sleep_counter_reset()
        fsm_state = 2
        
    if is_sleeping:
        wake_up()
    else:
        before_action = None
        after_action = None

        try:
            action = profile.actions[utt]
            answer = action[0]
            after_action = action[2]
        except KeyError as e:
            answer = 'unrecognized'

        print ("answer = " + answer)

        if ('rss' in answer) and (not 'start' in answer):
            try:
                fsm_state = fsm_transition[answer]
            except:
                fsm_state = 6
            
            profile.a_player.play_answer(answer)

            if after_action:
                after_action()
        # else:
        #     fsm_state = 1

    if sleep_enabled:
        sleep_counter_reset()

def get_confirmation(sphinx_proc):
    print ('Get confirmation mode:')

    utt = get_utterance(sphinx_proc)

    if speech_recognizer.lang == 'ru':
        try:
            utt = profile.STTTranslatorRU.tr_conversation_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))
    if utt == profile.confirmation_phrase:
        return True
    else:
        return False

def stop_pocketsphinx():
    stop_exe = 'killall -s STOP pocketsphinx_co'
    p = subprocess.Popen(["%s" % stop_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def cont_pocketsphinx():
    cont_exe = 'killall -s CONT pocketsphinx_co'
    p = subprocess.Popen(["%s" % cont_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

if __name__ == "__main__":
   main(sys.argv[1:])
