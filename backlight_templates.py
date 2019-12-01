# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

import os

eyes_off = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "off"]
eyes_on = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "on"]
teeth_off = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "off"]
teeth_on_ok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on"]
teeth_on_notok = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on", "-r", "255", "-g", "0"]

eyes_music = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "music"]
teeth_music = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "music"]

teeth_talk = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "talk"]

def backlight(backlight_command):
    global backlightEnabled
    if backlightEnabled:
        p = subprocess.Popen(backlight_command)
        return p
    else:
        return None

