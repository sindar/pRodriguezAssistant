# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

from pyModbusTCP.client import ModbusClient

def send_command(command):
    try:
        mb_connection = ModbusClient(host="192.168.43.136", auto_open=True, auto_close=True)
    except:
        print('Error opening ModBus TCP Connection!')
        return

    if command == 'on':
        mb_connection.write_single_register(10, 1)
    elif command == 'off':
        mb_connection.write_single_register(10, 2)
    elif command == 'red':
        mb_connection.write_multiple_registers(10, [1, 1, 255, 0, 0])
    elif command == 'green':
        mb_connection.write_multiple_registers(10, [1, 1, 0, 255, 0])
    elif command == 'blue':
        mb_connection.write_multiple_registers(10, [1, 1, 0, 0, 255])