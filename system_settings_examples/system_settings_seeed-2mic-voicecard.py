# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

RECORD_MIXER = 'Capture'
RECORD_DEVICE = None

SPEAKER_MIXER = 'Playback'
#The scale of the speaker voulme modes and step depends on device
SPEAKER_MODES = {
    'min': 0,
    'quiet': 180,
    'normal': 220,
    'loud': 240,
    'max': 255
}

VOLUME_STEP = (SPEAKER_MODES['max'] - SPEAKER_MODES['quiet']) / 10
