# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import threading
import sys
from common import power, ups_lite
from profiles.bender import bender as profile

main_thread_is_running = True

SLEEP_TASK_ENABLED = True
IDLE_TIME = 60 # in minutes, 2 - minimum
sleep_enabled = False
is_sleeping = False
sleep_counter = 0
sleep_counter_lock = threading.Lock()

UPS_TASK_ENABLED = True
UPS_TASK_INTERVAL = 2
if UPS_TASK_ENABLED: pass

fsm_state = 1
fsm_transition = {
    'keyphrase': 2,
    'exit': 3,
    'reboot': 4,
    'shutdown': 5
}

def sleep_enable_set(val):
    global sleep_enabled
    sleep_enabled = val

def main():
    global main_thread_is_running
    global fsm_state
    global sleep_enabled

    profile.vol_ctrl.set_speaker_volume(profile.vol_ctrl.speaker_volume)

    kill_pocketsphinx()
    profile.m_player.send_command('stop')

    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('OFF')
    time.sleep(0.15)

    if UPS_TASK_ENABLED:
        ups_thread = threading.Thread(target=ups_task)
        ups_thread.start()
        sleep_enabled = True

    if SLEEP_TASK_ENABLED:
        sleep_thread = threading.Thread(target=sleep_task)
        sleep_thread.daemon = True
        sleep_thread.start()

    sphinx_proc = subprocess.Popen(["%s" % profile.speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % profile.speech_recognizer.cmd_line])

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

    if profile.speech_recognizer.lang == 'ru':
        try:
            utt = profile.TranslatorRU.tr_start_ru_en[utt]
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

    print ('Conversation mode:')

    utt = get_utterance(sphinx_proc)

    if profile.speech_recognizer.lang == 'ru':
        try:
            utt = profile.TranslatorRU.tr_conversation_ru_en[utt]
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

        if before_action:
            before_action()
        if fsm_state != 2:
            if answer != 'no audio':
                profile.a_player.play_answer(answer)

            if after_action:
                after_action()
            if answer != 'shutdown' or answer != 'reboot':
                if profile.m_player.musicIsPlaying:
                    profile.m_player.send_command('resume')
    if sleep_enabled:
        sleep_counter_reset()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
