# !/usr/bin/env python
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import string

fsmState = 0

audio_files = {}
audio_files['shutdown'] = 'with_bjah'
audio_files['start'] = 'lets_get_drunk'
audio_files['exit'] = 'lets_get_drunk'
audio_files['hey bender 0'] = 'bite'
audio_files['hey bender 1'] = 'hello'
audio_files['hey bender 2'] = 'hello_peasants'
audio_files['birthplace'] = 'born_in_tijuana'
audio_files['birthdate'] = 'birthdate'
audio_files['who are you 0'] = 'im_bender'
audio_files['who are you 1'] = 'bender_song'
audio_files['animal'] = 'turtle'
audio_files['sing'] = 'bender_song'
audio_files['magnet 0'] = 'roads_song'
audio_files['magnet 1'] = 'mountain_song'
audio_files['new sweater'] = 'new_sweater'
audio_files['kill all humans'] = 'kill_all_humans'
audio_files['wake up'] = 'most_wonderful_dream'
audio_files['enable'] = 'can_do'
audio_files['disable'] = 'can_do'
audio_files['set'] = 'can_do'
audio_files['how are you'] = 'right_now_i_feel_sorry_for_you'
audio_files['configuration'] = 'can_do'
audio_files['unrecognized'] = 'beat_children'
audio_files['no audio'] = 'silence'

class PsLiveRecognizer:
    def __init__(self, resources_dir, parameter_set):
        self.resources_dir = resources_dir
        self.parameter_set = parameter_set
        self.generatePsCmdLine()

    def generatePsCmdLine(self):
        self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                        + ' -lm ' + self.resources_dir + self.parameter_set + '.lm' \
                        + ' -dict ' + self.resources_dir + self.parameter_set + '.dic' \
                        + ' -dictcase yes -inmic yes ' \
                        + '-logfn /dev/null' \
                        + ' -jsgf ' + self.resources_dir + self.parameter_set + '.gram' \

def main():
    global fsmState
    while True:
        if (fsmState == 0):
            start_mode()
        elif (fsmState == 1):
            conversation_mode()
        elif (fsmState ==2):
            configuration_mode()
        else:
            fsmState = 0

def start_mode():
    global fsmState
    ps = PsLiveRecognizer('./resources/', 'start')
    p = subprocess.Popen(["%s" % ps.cmd_line], shell=True, stdout=subprocess.PIPE)

    print(["%s" % ps.cmd_line])

    while True:
        print('Start mode:')
        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().lower()
        print('utterance = ' + utt)
        if ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
            command = 'hey bender ' + str(current_milli_time % 3)
            play_answer(command)
            fsmState = 1
        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 0):
            break
    kill_pocketsphinx()

def conversation_mode():
    global fsmState
    ps = PsLiveRecognizer('./resources/', 'conversation')
    p = subprocess.Popen(["%s" % ps.cmd_line], shell=True, stdout=subprocess.PIPE)

    print (["%s" % ps.cmd_line])

    while True:
        print ('Conversation mode:')
        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().lower()
        print('utterance = ' + utt)

        if 'shutdown' in utt:
            command = 'shutdown'
            fsmState = 0
        elif ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
            command = 'exit'
            fsmState = 0
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
            command = 'sweater'
        elif ('wake up' in utt) or ('awake' in utt):
            command = 'wake up'
        elif ('configuration' in utt) or ('configure' in utt):
            command = 'configuration'
            fsmState = 2
        else:
            command = 'unrecognized'
        play_answer(command)
        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 1):
            break
    kill_pocketsphinx()

def configuration_mode():
    global fsmState
    ps = PsLiveRecognizer('./resources/', 'configuration')
    p = subprocess.Popen(["%s" % ps.cmd_line], shell=True, stdout=subprocess.PIPE)

    print(["%s" % ps.cmd_line])

    while True:
        print('Configuration mode:')
        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().lower()
        print('utterance = ' + utt)

        if ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
            command = 'exit'
            fsmState = 0
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
    kill_pocketsphinx()

def kill_pocketsphinx():
    kill_exe = 'killall pocketsphinx_continuous'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def play_answer(command):
    global audio_files
    answer = audio_files.get(command)
    if answer != None:
        exe = 'aplay ' + './audio/' + answer + '.wav'
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()
    else:
        print('No answer to this question!')

main()
