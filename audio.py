# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

audio_files = {}
audio_files['shutdown'] = 'with_bjah'
audio_files['start'] = 'lets_get_drunk'
audio_files['exit'] = 'lets_get_drunk'
audio_files['hey bender 0'] = 'bite'
audio_files['hey bender 1'] = 'hello'
audio_files['hey bender 2'] = 'hello_peasants'
audio_files['birthplace'] = 'born_in_tijuana'
audio_files['birthdate'] = 'birthdate'
audio_files['who are you 0'] = 'im_bender'
audio_files['who are you 1'] = 'bender_song'
audio_files['animal'] = 'turtle'
audio_files['sing'] = 'bender_song'
audio_files['magnet 0'] = 'roads_song'
audio_files['magnet 1'] = 'mountain_song'
audio_files['new sweater'] = 'new_sweater'
audio_files['kill all humans'] = 'kill_all_humans'
audio_files['wake up'] = 'most_wonderful_dream'
audio_files['enable'] = 'can_do'
audio_files['disable'] = 'can_do'
audio_files['set'] = 'can_do'
audio_files['how are you'] = 'right_now_i_feel_sorry_for_you'
audio_files['configuration'] = 'can_do'
audio_files['player'] = 'can_do'
audio_files['unrecognized'] = 'silence'
audio_files['no audio'] = 'silence'

def play_answer(command):
    global audio_files
    global teeth_off
    global audio_lang

    answer = audio_files.get(command)
    if answer != None:
        if (command == 'unrecognized'):
            backlight(teeth_on_notok)
        else:
            mic_set(0)

            exe = 'play ' + './audio/' + audio_lang + '/' + answer + '.ogg'

            bl_proc = backlight(teeth_talk)
            time.sleep(0.5)

            p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
            code = p.wait()
            bl_proc.kill()
            mic_set(micGain)
        backlight(teeth_off)
    else:
        print('No answer to this question!')

def mic_set(val):
    exe = "amixer -q -c 1 sset 'Mic' " + str(val)
    p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()
