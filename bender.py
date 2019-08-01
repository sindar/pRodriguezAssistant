# !/usr/bin/env python
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import string

def main():
    exe = '''pocketsphinx_continuous -adcdev plughw:1,0  -lm ./resources/bender.lm -dict ./resources/bender.dic''' + \
          ''' -jsgf ./resources/bender.gram -dictcase yes -inmic yes'''
    # '''./resources/bender.gram -dictcase yes -inmic yes -logfn /dev/null'''
    p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)

    while True:
        retcode = p.returncode
        line = p.stdout.readline()
        print ("utterance = " + line)
        command = parse_utterance(string.lower(line))
        print ("command = " + command)
        time.sleep(0.15)
        if (retcode is not None):
            break


def parse_utterance(utt):
    if 'shutdown' in utt:
        command = 'shutdown'
    elif ('exit' in utt) or ('quit' in utt) :
        command = 'exit'
    elif ('sing' in utt) or ('song' in utt):
        command = 'sing'
    elif 'who are you' in utt:
        command = 'who are you'
    elif 'how are you' in utt:
        command = 'how are you'
    elif ('where are you from' in utt) or ('where were you born' in utt):
        command = 'birthplace'
    elif 'when were you born' in utt:
        command = 'birthdate'
    elif 'your favorite animal' in utt:
        command = 'animal'
    elif ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
        command = 'hey bender'
    elif 'magnet' in utt:
        command = 'magnet'
    elif 'new sweater' in utt:
        command = 'sweater'
    elif ('wake up' in utt) or ('awake' in utt):
        command = 'wake up'
    else:
        command = 'unrecognized'
    return command

main()


