# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import os
import time

audio_lang = 'ru'
recognize_lang ='ru'
backlightEnabled = True
sleepEnabled = True


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

class AnswerPlayer:
    def __init__(self):
        self.mic_gain = 80
        self.mic_set(self.mic_gain)

    def play_answer(self, command):
        global audio_files
        global teeth_off
        global audio_lang

        answer = audio_files.get(command)
        if answer != None:
            if (command == 'unrecognized'):
                backlight(teeth_on_notok)
            else:
                self.mic_set(0)

                exe = 'play ' + './audio/' + audio_lang + '/' + answer + '.ogg'

                bl_proc = backlight(teeth_talk)
                time.sleep(0.5)

                p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
                code = p.wait()
                bl_proc.kill()
                self.mic_set(self.mic_gain)
            backlight(teeth_off)
        else:
            print('No answer to this question!')

    def mic_set(self, val):
        exe = "amixer -q -c 1 sset 'Mic' " + str(val)
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()

eyes_off = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "off"]
eyes_on = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "on"]
teeth_off = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "off"]
teeth_on_ok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on"]
teeth_on_notok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on", "-r", "255", "-g", "0"]

eyes_music = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "music"]
teeth_music = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "music"]

teeth_talk = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "talk"]

def backlight(backlight_command):
    global backlightEnabled
    if backlightEnabled:
        p = subprocess.Popen(backlight_command)
        return p
    else:
        return None