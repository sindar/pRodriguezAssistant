# !/usr/bin/env python
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import os
from threading import Timer

SLEEPING_TIME = 600.0

fsmState = 0
audio_lang = 'ru'
recognize_lang ='ru'
backlightEnabled = True
sleepEnabled = True
isSleeping = False
micGain = 80

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
audio_files['player'] = 'can_do'
audio_files['unrecognized'] = 'silence'
audio_files['no audio'] = 'silence'

tr_start_ru_en  = {
    u'бендер': 'bender',
    u'привет бендер': 'hi bender',
    u'эй бендер': 'hi bender',
}

tr_conversation_ru_en = {
    u'включи музыкальный плеер': 'enable music player',
    u'отключи музыкальный плеер': 'disable music player',
    u'спой песню': 'sing song',
    u'конфигурация': 'configure',
    u'откуда ты': 'where are you from',
    u'где ты родился': 'where were you born',
    u'когда ты родился': 'when were you born',
    u'дата рождения': 'when were you born',
    u'какое твоё любимое животное': 'your favorite animal',
    u'какой твой любимый зверь': 'your favorite animal',
    u'кто ты': 'who are you',
    u'как ты': 'how are you',
    u'как поживаешь': 'how are you',
    u'магнит': 'magnet',
    u'хороший новый свитер': 'new sweater',
    u'выключение': 'shutdown',
    u'стоп': 'stop',
    u'пока': 'stop'
}

tr_configuration_ru_en = {
    u'сон': 'sleep',
    u'засыпание': 'sleep',
    u'выход': 'exit',
    u'закрой': 'exit',
    u'включи': 'enable',
    u'выключи': 'disable',
    u'в': 'to',
    u'магнит': 'magnet'
}

tr_player_ru_en  = {
    u'отключи музыкальный плеер': 'disable music player'
}

eyes_off = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "off"]
eyes_on = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "on"]
teeth_off = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "off"]
teeth_on_ok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on"]
teeth_on_notok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on", "-r", "255", "-g", "0"]

eyes_music = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "music"]
teeth_music = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "music"]

teeth_talk = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "talk"]

class PsLiveRecognizer:
    global recognize_lang
    lang = recognize_lang
    def __init__(self, resources_dir, parameter_set):
        self.resources_dir = resources_dir
        self.parameter_set = parameter_set
        self.generatePsCmdLine()

    def generatePsCmdLine(self):
        if self.lang == 'en':
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                        + ' -lm ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.lm' \
                        + ' -dict ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.dic' \
                        + ' -dictcase yes -inmic yes ' \
                        + ' -jsgf ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.jsgf'
                        #+ ' -logfn /dev/null ' \
        else:
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                            + ' -hmm ' + self.resources_dir + self.lang + '/lm/zero_ru.cd_semi_4000/' \
                            + ' -dict ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.dic' \
                            + ' -dictcase yes -inmic yes ' \
                            + ' -jsgf ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.jsgf'
                            #+ ' -logfn /dev/null ' \
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
    backlight(eyes_on)

    mic_set(micGain)

    ps = PsLiveRecognizer('./resources/', 'bender')
    p = subprocess.Popen(["%s" % ps.cmd_line], shell=True, stdout=subprocess.PIPE)

    print(["%s" % ps.cmd_line])

    while True:
        if (fsmState == 0):
            start_mode(p)
        elif (fsmState == 1):
            conversation_mode(p)
        elif (fsmState == 2):
            configuration_mode(p)
        elif (fsmState == 3):
            player_mode(p)
        elif (fsmState == 4):
            break
        else:
            fsmState = 0

    kill_pocketsphinx()
    backlight(eyes_off)

def sleep_timeout():
    global isSleeping
    play_answer('kill all humans')
    isSleeping = True

def start_mode(p):
    global fsmState
    global sleepEnabled

    while True:
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
            if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
                command = 'hey bender ' + str(current_milli_time % 3)
                play_answer(command)
            else:
                fsmState = 1

        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 0):
            break

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

        fsmState = 0
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
            command = 'player'
            #fsmState = 3
        else:
            command = 'unrecognized'
        play_answer(command)

        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 1):
            break

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

def player_mode(p):
    global fsmState

    play_exe = 'find /home/pi/music -iname "*.mp3" | mpg123 -m -Z --list -'
    player = subprocess.Popen(["%s" % play_exe], shell=True, stdout=subprocess.PIPE)

    bl_proc = backlight(teeth_music)

    while True:
        print('Player mode:')
        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if PsLiveRecognizer.lang == 'ru':
            try:
                utt = tr_player_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if ('disable music player' in utt):
            kill_player()
            command = 'player'
            play_answer(command)
            fsmState = 1
        time.sleep(0.15)
        if (fsmState != 3):
            if bl_proc:
                bl_proc.kill()
            break

def kill_pocketsphinx():
    kill_exe = 'killall pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def kill_player():
    kill_exe = 'killall mpg123'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def mic_set(val):
    exe = "amixer -q -c 1 sset 'Mic' " + str(val)
    p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def play_answer(command):
    global audio_files
    global teeth_on
    global teeth_off
    global audio_lang

    answer = audio_files.get(command)
    if answer != None:
        if (command == 'unrecognized'):
            backlight(teeth_on_notok)
        else:
            mic_set(0)

            exe = 'play ' + './audio/' + audio_lang + '/' + answer + '.ogg'

            bl_proc = backlight(teeth_talk)
            time.sleep(0.5)

            p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
            code = p.wait()
            bl_proc.kill()
            mic_set(micGain)
        backlight(teeth_off)
    else:
        print('No answer to this question!')

def backlight(backlight_command):
    global backlightEnabled
    if backlightEnabled:
        p = subprocess.Popen(backlight_command)
        return p
    else:
        return None

main()
