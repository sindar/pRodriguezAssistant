# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

from pyModbusTCP.client import ModbusClient

def send_command(switch):
    try:
        mb_connection = ModbusClient(host="192.168.43.136", auto_open=True, auto_close=True)
    except:
        print('Error opening ModBus TCP Connection!')
        return

    if switch == 'on':
        mb_connection.write_single_register(10, 1)
    if switch == 'off':
        mb_connection.write_single_register(10, 0)
    