# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import system_settings as sys_set

class VolumeControl:
    def __init__(self):
        self.modes = sys_set.SPEAKER_MODES
        self.speaker_volume = self.modes['normal']
        self.VOLUME_STEP = sys_set.VOLUME_STEP

    def change_speaker_volume(self, value):
        speaker_volume = self.speaker_volume + value
        if speaker_volume < self.modes['min']:
            speaker_volume = self.modes['min']
        if speaker_volume > self.modes['max']:
            speaker_volume = self.modes['max']
        self.set_speaker_volume(speaker_volume)

    def set_speaker_volume(self, value):
        print("volume = " + str(value))
        print("self.volume = " + str(self.speaker_volume))
        self.speaker_volume = value
        amixer_exe = "amixer -q -c 1 sset " + sys_set.SPEAKER_MIXER + ' ' + str(value)
        p = subprocess.Popen(["%s" % amixer_exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()