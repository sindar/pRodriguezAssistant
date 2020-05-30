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
import volume_control as vol_ctrl

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

exit_utts1 = [exit_utts + ' program' for exit_utts in ['quit', 'exit']]
exit_utts2 = [exit_utts + ' the program' for exit_utts in ['quit', 'exit']]
exit_actions = {
    **dict.fromkeys(exit_utts1, ['exit', lambda: update_fsm(3), None]),
    **dict.fromkeys(exit_utts2, ['exit', lambda: update_fsm(3), None])
}

mode_actions = {
    'quiet mode': ['configuration',
                   lambda: vol_ctrl.set_speaker_volume(vol_ctrl.modes['quiet']), None],
    'normal mode': ['configuration',
                    lambda: vol_ctrl.set_speaker_volume(vol_ctrl.modes['normal']), None],
    'loud mode': ['configuration',
                  lambda: vol_ctrl.set_speaker_volume(vol_ctrl.modes['loud']), None]
}

volume_actions = {
    **dict.fromkeys(['louder', 'increase volume'], ['configuration',
               lambda: vol_ctrl.change_speaker_volume(vol_ctrl.VOLUME_STEP), None]),
    **dict.fromkeys(['quieter', 'decrease volume'], ['configuration',
               lambda: vol_ctrl.change_speaker_volume(-vol_ctrl.VOLUME_STEP), None])
}

power_actions = {
    'shutdown': ['shutdown', lambda: update_fsm(4), None],
    'reboot': ['reboot', lambda: update_fsm(5), None],
}

only_answer_actions = {
    **dict.fromkeys(['sing song', 'sing a song'], ['sing', None, None]),
    **dict.fromkeys(['what do you think about ' + name
                     for name in ['alexa', 'alice', 'cortana', 'siri']],
                    ['bad girl', None, None]),
    'who are you': ['who are you', None, None],
    'how are you': ['how are you', None, None],
    'where are you from': ['birthplace', None, None],
    'when were you born': ['birthdate', None, None],
    'what is your favorite animal': ['animal', None, None],
    'how can you live without a body': ['body', None, None],
    'magnet': ['magnet', None, None],
    'a great new sweater': ['new sweater', None, None],
}

player_actions = {
    **dict.fromkeys(['start player', 'start the player'],
                    ['player', None, lambda: m_player.send_command('start')]),
    **dict.fromkeys(['stop player', 'stop the player'],
                    ['player', None, lambda: m_player.send_command('stop')]),
    **dict.fromkeys(['next song', 'next track'],
                    ['no audio', None, lambda: m_player.send_command('next')])
}

sleep_actions = {
    'enable sleep': ['configuration', None, lambda: sleep_enable_set(True)],
    'disable sleep': ['configuration', None, lambda: sleep_enable_set(False)]
}

repeated_keyphrase_actions = {
    **dict.fromkeys([prefix + ' bender'
                    for prefix in ['hi','hey','hello','stop','pause']],
                    ['no audio', lambda: update_fsm(2), None]),
    **dict.fromkeys(['bender ' + suffix
                    for suffix in ['hi', 'hey', 'hello', 'stop', 'pause']],
                    ['no audio', lambda: update_fsm(2), None])
}

actions = {
    **exit_actions,
    **mode_actions,
    **volume_actions,
    **power_actions,
    **only_answer_actions,
    **player_actions,
    **sleep_actions,
    **repeated_keyphrase_actions
}

def sleep_enable_set(val):
    global sleep_enabled
    sleep_enabled = val

def update_fsm(new_state):
    global fsm_state
    fsm_state = new_state

def main():
    global fsm_state
    global m_player
    global speech_recognizer
    global main_thread_is_running

    vol_ctrl.set_speaker_volume(vol_ctrl.speaker_volume)

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
            if('pause' in utt or 'stop' in utt or vol_ctrl.speaker_volume == 0):
                m_player.send_command('pause')
                keyphrase_found = True
        else:
            if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)) and not is_sleeping:
                answer = 'hey bender'
                a_player.play_answer(answer)
            if is_sleeping:
                wake_up()
            keyphrase_found = True

    return keyphrase_found

def conversation_mode(sphinx_proc):
    global fsm_state
    global sleep_enabled
    global is_sleeping
    global a_player

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
        after_action = None

        try:
            action = actions[utt]
            answer = action[0]
            before_action = action[1]
            after_action = action[2]
        except KeyError as e:
            answer = 'unrecognized'

        print ("answer = " + answer)

        if before_action:
            before_action()
        if fsm_state != 2:
            if answer != 'no audio':
                a_player.play_answer(answer)

            if after_action:
                after_action()
            if answer != 'shutdown' or answer != 'reboot':
                if m_player.musicIsPlaying:
                    m_player.send_command('resume')
    sleep_counter_reset()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
