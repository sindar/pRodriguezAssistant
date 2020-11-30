# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import system_settings as sys_set
import os

class AnswerPlayer:
    lang = 'en'
    def __init__(self, profile_path, lang, answers, tts_cmd, mouth_bl, eyes_bl):
        self.mic_gain = 30
        self.mic_set(self.mic_gain)
        self.profile_path = profile_path
        self.audio_path = profile_path + '/audio/'
        self.tts_cmd = tts_cmd
        self.eyes_bl = eyes_bl
        self.mouth_bl = mouth_bl
        if self.mouth_bl:
            self.mouth_bl.exec_cmd('OFF')
        self.answers = answers
        AnswerPlayer.lang = lang

    def calc_answer(self, answers):
        if answers != None:
            if type(answers) is tuple:
                r_count = len(answers)
                if r_count > 1:
                    answer = answers[int(round(time.time() * 1000)) % r_count]
            else:
                answer = answers
        return answer

    def play_answer(self, command):

        if command == 'electricity':
            bl_command = 'PLUGGED_IN'
        else:
            bl_command = 'TALK'

        answers = self.answers.get(command)

        # Look for a wav-file first
        answer_wav = self.calc_answer(answers[0])
        wav_path = self.audio_path + AnswerPlayer.lang + '/' + answer_wav + '.wav'
        self.mic_set(0)
        
        if os.path.exists(wav_path):
            aplay_exe = 'aplay -Dplug:default ' + str(wav_path)
            aplay_proc = subprocess.Popen(["%s" % aplay_exe], shell=True, stdout=subprocess.PIPE)
            delay = None
        else:
            answer_tts = self.calc_answer(answers[1])
            aplay_exe = self.tts_cmd  + '"' + answer_tts + '"'             
            aplay_proc = subprocess.Popen(["%s" % aplay_exe], shell=True, stdout=subprocess.PIPE)
            delay = 0.5

        eyes_bl_proc = None
        mouth_bl_proc = None
        if self.mouth_bl:
            mouth_bl_proc = self.mouth_bl.exec_cmd(bl_command, delay)
        if self.eyes_bl:
            if bl_command == 'PLUGGED_IN':
                eyes_bl_proc = self.eyes_bl.exec_cmd('BLINK_PLUGGED_IN', delay)

        code = aplay_proc.wait()

        if mouth_bl_proc:
            mouth_bl_proc.terminate()
        if eyes_bl_proc:
            eyes_bl_proc.terminate()
            self.eyes_bl.exec_cmd('ON')

        self.mic_set(self.mic_gain)
        if self.mouth_bl:
            self.mouth_bl.exec_cmd('OFF')

    def mic_set(self, val):
        exe = 'amixer -q -c 1 sset ' + sys_set.RECORD_MIXER + ' ' + str(val)
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()
