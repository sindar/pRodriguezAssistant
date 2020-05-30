# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess

modes = {
    'quiet': 8,
    'normal': 20,
    'loud': 32
}

speaker_volume = 20
VOLUME_STEP = 4

def change_speaker_volume(value):
    global speaker_volume

    speaker_volume += value
    if speaker_volume < 0:
        speaker_volume = 0
    if speaker_volume > 40:
        speaker_volume = 40
    set_speaker_volume(speaker_volume)

def set_speaker_volume(value):
    amixer_exe = "amixer -q -c 1 sset 'Speaker' " + str(value)
    p = subprocess.Popen(["%s" % amixer_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()