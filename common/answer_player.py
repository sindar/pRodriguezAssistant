# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import system_settings as sys_set
import os

class AnswerPlayer:
    lang = 'en'
    def __init__(self, profile_path, lang, answers, cloud_tts, offline_tts, mouth_bl, eyes_bl):
        self.mic_gain = 30
        self.mic_set(self.mic_gain)
        self.profile_path = profile_path
        self.audio_path = profile_path + '/audio/'
        self.cloud_tts = cloud_tts
        self.offline_tts = offline_tts
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

    def play_wav(self, path):
        aplay_exe = 'aplay -Dplug:default ' + str(path)
        return subprocess.Popen(["%s" % aplay_exe], shell=True, stdout=subprocess.PIPE)

    def play_tts(self, sentence):
        wav_path = None
        if self.cloud_tts:
            wav_path = self.cloud_tts.text_to_speech(sentence)
        else:
            wav_path = '/dev/shm/offline_tts.wav'
            tts_exe = self.offline_tts + wav_path + ' "' + sentence + '"'
            tts_proc = subprocess.Popen(["%s" % tts_exe], shell=True, stdout=subprocess.PIPE)
            code = tts_proc.wait()

        aplay_proc = self.play_wav(wav_path)
        return aplay_proc

    def play_answer(self, command, sentence = None):
        if command != None:
            answers = self.answers.get(command)
            if answers[0] == None and answers[1] == None:
                return

            if command == 'electricity':
                bl_command = 'PLUGGED_IN'
            else:
                bl_command = 'TALK'

            # Look for the wav-file first
            answer_wav = self.calc_answer(answers[0])
            wav_path = self.audio_path + AnswerPlayer.lang + '/' + answer_wav + '.wav'

            if os.path.exists(wav_path):
                self.mic_set(0)
                aplay_proc = self.play_wav(wav_path)
                delay = None
            else:
                self.mic_set(0)
                answer_tts = self.calc_answer(answers[1])
                # Second, trying the cloud TTS
                aplay_proc = self.play_tts(answer_tts)
                delay = None
        else:
            if sentence:
                # Directly speak the sentence:
                self.mic_set(0)
                self.mouth_bl.exec_cmd('ON')
                aplay_proc = self.play_tts(sentence)
                bl_command = 'TALK'
                delay = None

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
