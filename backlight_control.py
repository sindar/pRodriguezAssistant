# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import os
import subprocess
import psutil
import board
import neopixel
import sys
import getopt
import time
import random
import math

eyes_pin = board.D21
teeth_pin = board.D18

eyes_num = 1 # two eyes in parallel
teeth_num = 18

ORDER = neopixel.GRB

default_color = (243, 253, 0)
no_color = (0, 0, 0)
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

class BackLightCommands:
    EYES_OFF = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "off"]
    EYES_ON = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "on"]
    TEETH_OFF = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "off"]
    TEETH_ON_OK = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on"]
    TEETH_ON_NOT_OK = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "on", "-r", "255", "-g", "0"]

    EYES_MUSIC = ["python3", os.getcwd() + "/backlight.py", "-l", "eyes", "-s", "music"]
    TEETH_MUSIC = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "music"]

    TEETH_TALK = ["python3", os.getcwd() + "/backlight.py", "-l", "teeth", "-s", "talk"]

class BacklightControl:
    backlightEnabled = True

    @staticmethod
    def backlight(backlight_command):
        if BacklightControl.backlightEnabled:
            backlight_pids = [process.pid for process in psutil.process_iter() if
                         'python' in str(process.name) and 'backlight' in str(process.cmdline())]
            BacklightControl.kill_backlight(backlight_pids)
            p = subprocess.Popen(backlight_command)
            return p
        else:
            return None

    @staticmethod
    def kill_backlight(backlight_pids):
        for pid in backlight_pids:
            kill_exe = 'killall -s SIGKILL ' + str(pid)
            p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
            code = p.wait()