# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import simpleaudio
import time
from backlight_control import BacklightControl

audio_files = {}
audio_files['shutdown'] = 'with_bjah'
audio_files['start'] = 'lets_get_drunk'
audio_files['exit'] = 'lets_get_drunk'
audio_files['hey bender'] = ('bite', 'hello', 'hello_peasants')
audio_files['birthplace'] = 'born_in_tijuana'
audio_files['birthdate'] = 'birthdate'
audio_files['who are you'] = ('im_bender', 'bender_song')
audio_files['animal'] = 'turtle'
audio_files['body'] = 'bodies'
audio_files['bad girl'] = 'bad_girl'
audio_files['sing'] = 'bender_song'
audio_files['magnet'] = ('roads_song', 'mountain_song')
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
    lang = 'en'
    def __init__(self, lang):
        self.mic_gain = 40
        self.mic_set(self.mic_gain)
        self.mouth_bl = BacklightControl('MOUTH')
        self.mouth_bl.exec_cmd('OFF')
        AnswerPlayer.lang = lang

    def play_wav(self, path):
        wave_obj = simpleaudio.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        p = self.mouth_bl.exec_cmd('TALK')
        play_obj.wait_done()
        p.terminate()

    def play_answer(self, command):
        answer = audio_files.get(command)
        if answer != None:
            if (command == 'unrecognized'):
                a = 1
                # BacklightControl.backlight(BackLightCommands.TEETH_ON_NOT_OK)
            else:
                if type(answer) is tuple:
                    a_count = len(answer)
                    if a_count > 1:
                        answer = answer[int(round(time.time() * 1000)) % a_count]
                else:
                    answer = answer

                self.mic_set(0)
                self.play_wav('./audio/' + AnswerPlayer.lang + '/' + answer + '.wav')
                self.mic_set(self.mic_gain)
            self.mouth_bl.exec_cmd('OFF')
        else:
            print('No answer to this question!')

    def mic_set(self, val):
        exe = "amixer -q -c 1 sset 'Mic' " + str(val)
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()
