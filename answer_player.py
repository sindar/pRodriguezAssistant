# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
from backlight_control import BacklightControl
from backlight_control import BackLightCommands
import simpleaudio as sa

import board
import neopixel
import math
from concurrent.futures import ThreadPoolExecutor

default_color = (243, 253, 0)
no_color = (0, 0, 0)
eyes_pin = board.D21
teeth_pin = board.D18
eyes_num = 1 # two eyes in parallel
teeth_num = 18
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

ORDER = neopixel.GRB

audio_files = {}
audio_files['shutdown'] = 'with_bjah'
audio_files['start'] = 'lets_get_drunk'
audio_files['exit'] = 'lets_get_drunk'
audio_files['hey bender 0'] = 'bite'
# audio_files['hey bender 1'] = 'hello'
audio_files['hey bender 1'] = 'hello_peasants'
# audio_files['hey bender 2'] = 'hello_peasants'
audio_files['birthplace'] = 'born_in_tijuana'
audio_files['birthdate'] = 'birthdate'
audio_files['who are you 0'] = 'im_bender'
audio_files['who are you 1'] = 'bender_song'
audio_files['animal'] = 'turtle'
audio_files['body'] = 'bodies'
audio_files['bad girl'] = 'bad_girl'
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
    lang = 'en'
    def __init__(self, lang):
        self.mic_gain = 40
        self.mic_set(self.mic_gain)
        self.pixels = neopixel.NeoPixel(teeth_pin, teeth_num, brightness=0.5, auto_write=False,
                                   pixel_order=ORDER)
        self.is_playing = False
        AnswerPlayer.lang = lang

    def play_wav(self, path):
        self.is_playing = True
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        self.is_playing = False

    def play_answer(self, command):
        answer = audio_files.get(command)
        if answer != None:
            if (command == 'unrecognized'):
                a = 1
                # BacklightControl.backlight(BackLightCommands.TEETH_ON_NOT_OK)
            else:
                self.mic_set(0)

                # self.switch_pixels(True)
                # wave_obj = sa.WaveObject.from_wave_file('./audio/' + AnswerPlayer.lang + '/' + answer + '.wav')
                # play_obj = wave_obj.play()
                # play_obj.wait_done()  # Wait until sound has finished playing

                with ThreadPoolExecutor(max_workers=2) as executor:
                    executor.submit(self.play_wav, './audio/' + AnswerPlayer.lang + '/' + answer + '.wav')
                    executor.submit(self.math_talk)


                #exe = 'play ' + './audio/' + AnswerPlayer.lang + '/' + answer + '.ogg'

                # BacklightControl.backlight(BackLightCommands.TEETH_ON_OK)
                # bl_proc = BacklightControl.backlight(BackLightCommands.TEETH_TALK)
                #time.sleep(0.5)

                #p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
                #code = p.wait()
                # bl_proc.kill()
                self.mic_set(self.mic_gain)
            self.switch_pixels(False)
            # BacklightControl.backlight(BackLightCommands.TEETH_OFF)
        else:
            print('No answer to this question!')

    def mic_set(self, val):
        exe = "amixer -q -c 1 sset 'Mic' " + str(val)
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()

    def switch_pixels(self, on):
        if on:
            self.pixels.fill(default_color)
        else:
            self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def math_talk(self):
        while self.is_playing:
            self.pixels.fill((0, 0, 0))
            for i in range(6, 12):
                self.pixels[i] = default_color
            self.pixels.show()
            time.sleep(0.25)

            self.sin_cos_graph(math.cos)
            time.sleep(0.25)

            self.pixels.fill((0, 0, 0))
            for i in range(6, 12):
                self.pixels[i] = default_color
            self.pixels.show()
            time.sleep(0.25)

            self.sin_cos_graph(math.sin)
            time.sleep(0.25)

    def sin_cos_graph(self, func):
        if func != math.sin and func != math.cos:
            return
        self.pixels.fill((0, 0, 0))
        t = 0
        for x in range(0, 6):
            y = func(t)
            j = x
            if y >= -1 and y < -0.33:
                i = 0
            elif y >= -0.33 and y < 0.33:
                i = 1
                j = revert_row1[x]
            else:
                i = 2
            c = i * 6 + j
            self.pixels[c] = default_color
            t += 1.57
        self.pixels.show()