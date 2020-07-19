# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import system_settings as sys_set

modes = sys_set.SPEAKER_MODES
speaker_volume = modes['normal']
VOLUME_STEP = sys_set.VOLUME_STEP

def change_speaker_volume(value):
    global speaker_volume

    speaker_volume += value
    if speaker_volume < modes['min']:
        speaker_volume = modes['min']
    if speaker_volume > modes['max']:
        speaker_volume = modes['max']
    set_speaker_volume(speaker_volume)

def set_speaker_volume(value):
    amixer_exe = "amixer -q -c 1 sset " + sys_set.SPEAKER_MIXER + ' ' + str(value)
    p = subprocess.Popen(["%s" % amixer_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()