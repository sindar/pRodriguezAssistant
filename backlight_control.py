# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import os
import subprocess
import psutil

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