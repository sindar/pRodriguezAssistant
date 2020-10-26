# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
from common import volume_control
from common import mbtcp_light
import pathlib
import time

name = 'bender'
audio_lang = 'en'
recognize_lang ='en'
sleep_enable_set = None
confirmation_phrase = 'please'
vol_ctrl = volume_control.VolumeControl()

BACKLIGHT_ENABLED = True
SLEEP_TASK_ENABLED = True
UPS_TASK_ENABLED = True

def calc_confirmation():
    if (time.monotonic_ns() % 3) == 0:
        return True

audio_files = {
    **dict.fromkeys(['reboot', 'shutdown'], ('with_bjah1', 'with_bjah2')),
    'exit': 'lets_get_drunk',
    'confirmation': 'dream_on_skintube',
    'confirmed': 'allright',
    'hey bender': ('bite', 'hello', 'hello_peasants'),
    'birthplace': 'born_in_tijuana',
    'birthdate': 'birthdate',
    'who are you': ('im_bender', 'bender_song', 'my_name_is_coilette'),
    'animal': 'turtle',
    'body': 'bodies',
    'bad girl': 'bad_girl',
    'sing': 'bender_song',
    'magnet': ('roads_song', 'mountain_song'),
    'new sweater': 'new_sweater',
    'fall asleep': ('kill_all_humans_1', 'kill_all_humans_2'),
    'wake up': 'most_wonderful_dream',
    **dict.fromkeys(['enable', 'disable','set', 'configuration', 'player'], ('can_do', 'yes_sir')),
    'how are you': ('none_of_your_business', 'right_now_i_feel_sorry_for_you', 'so_embarrassed'),
    'electricity': 'plugged_in',
    'unrecognized': ('beat_children', 'compare_your_lives_to_mine'),
    'repeated keyphrase': 'im_in_a_hurry',
    'wait you are serious': 'ow_wait_youre_serious',
    'laugh': 'laugh',
    'no audio': 'silence'
}

exit_actions = {
    **dict.fromkeys([exit_utts + ' program' for exit_utts in ['quit', 'exit', 'quit the', 'exit the']],
                    ['exit', None, None])
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
    'shutdown': ['shutdown', None, None],
    'reboot': ['reboot', None, None],
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
    **dict.fromkeys(['i am sad',"i'm sad", 'i am very sad', "i'm very sad", 'i am so sad', "i'm so sad"],
                    ['wait you are serious', None, None]),
    **dict.fromkeys(['you are bad',"you're bad", 'you are very bad', "you're very bad", 'you are so bad',
                     "you're so bad", 'you are cruel', "you're cruel", 'you are so cruel', "you're so cruel",
                     'you are evil', "you're evil", 'you are so evil', "you're so evil"],
                    ['laugh', None, None])
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
    'bender': ['repeated keyphrase', None, None],
    **dict.fromkeys([prefix + ' bender'
                    for prefix in ['hi','hey','hello','stop','pause']],
                    ['repeated keyphrase', None, None]),
    **dict.fromkeys(['bender ' + suffix
                    for suffix in ['hi', 'hey', 'hello', 'stop', 'pause']],
                    ['repeated keyphrase', None, None])
}

mbtcp_light_actions = {
    'turn on the light': ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('on')],
    'turn off the light': ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('off')],
    **dict.fromkeys(['turn on the red light', 'set the light to red'],
                    ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('red')]),
    **dict.fromkeys(['turn on the green light', 'set the light to green'], 
                    ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('green')]),
    **dict.fromkeys(['turn on the blue light', 'set the light to blue'],
                    ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('blue')]),
    'set the light to default': ['configuration', lambda: calc_confirmation(), lambda: mbtcp_light.send_command('on')]
}

actions = {
    **exit_actions,
    **mode_actions,
    **volume_actions,
    **power_actions,
    **only_answer_actions,
    **player_actions,
    **sleep_actions,
    **repeated_keyphrase_actions,
    **mbtcp_light_actions
}

from common.music_player import MusicPlayer
from common.answer_player import AnswerPlayer
from common.speech_recognizer import PsLiveRecognizer

if recognize_lang == 'ru':
    from profiles.bender.translation_ru import TranslatorRU

if BACKLIGHT_ENABLED:
    from profiles.bender.bender_backlight import BacklightControl
    eyes_bl = BacklightControl('EYES')
    mouth_bl = BacklightControl('MOUTH')
else:
    eyes_bl = None
    mouth_bl = None

a_player = AnswerPlayer(str(pathlib.Path(__file__).parent.absolute()) + '/audio/',
                        audio_lang, audio_files, eyes_bl=eyes_bl, mouth_bl=mouth_bl)
m_player = MusicPlayer()
