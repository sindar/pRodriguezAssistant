# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

RECORD_MIXER = 'Mic'
RECORD_DEVICE = 'plughw:1,0' #example: plughw:1,0

SPEAKER_MIXER = 'Speaker'
#The scale of the speaker voulme modes and step depends on device
SPEAKER_MODES = {
    'min': 0,
    'quiet': 8,
    'normal': 20,
    'loud': 32,
    'max': 40
}

VOLUME_STEP = (SPEAKER_MODES['max'] - SPEAKER_MODES['min']) / 10
