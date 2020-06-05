# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess

def shutdown():
    shutdown = "shutdown -Ph now"
    p = subprocess.Popen(["%s" % shutdown], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def reboot():
    reboot = "reboot"
    p = subprocess.Popen(["%s" % reboot], shell=True, stdout=subprocess.PIPE)
    code = p.wait()