# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time

class AnswerPlayer:
    lang = 'en'
    def __init__(self, lang, audio_files, mouth_bl, eyes_bl):
        self.mic_gain = 40
        self.mic_set(self.mic_gain)
        self.eyes_bl = eyes_bl
        self.mouth_bl = mouth_bl
        if self.mouth_bl:
            self.mouth_bl.exec_cmd('OFF')
        self.audio_files = audio_files
        AnswerPlayer.lang = lang

    def play_wav(self, path, bl_command):
        aplay_exe = 'aplay -Dplug:default ' + str(path)
        aplay_proc = subprocess.Popen(["%s" % aplay_exe], shell=True, stdout=subprocess.PIPE)

        eyes_bl_proc = None
        mouth_bl_proc = None
        if self.mouth_bl:
            mouth_bl_proc = self.mouth_bl.exec_cmd(bl_command)
        if self.eyes_bl:
            if bl_command == 'PLUGGED_IN':
                eyes_bl_proc = self.eyes_bl.exec_cmd('BLINK_PLUGGED_IN')

        code = aplay_proc.wait()

        if mouth_bl_proc:
            mouth_bl_proc.terminate()
        if eyes_bl_proc:
            eyes_bl_proc.terminate()
            self.eyes_bl.exec_cmd('ON')

    def play_answer(self, command):
        answer = self.audio_files.get(command)
        if answer != None:
            if type(answer) is tuple:
                a_count = len(answer)
                if a_count > 1:
                    answer = answer[int(round(time.time() * 1000)) % a_count]
            else:
                answer = answer

            if answer == 'plugged_in':
                bl_command = 'PLUGGED_IN'
            else:
                bl_command = 'TALK'

            self.mic_set(0)
            self.play_wav('./audio/' + AnswerPlayer.lang + '/' + answer + '.wav', bl_command)
            self.mic_set(self.mic_gain)
            if self.mouth_bl:
                self.mouth_bl.exec_cmd('OFF')
        else:
            print('No answer to this question!')

    def mic_set(self, val):
        exe = "amixer -q -c 1 sset 'Mic' " + str(val)
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
        code = p.wait()
