# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import board
import neopixel
import time
import math
from multiprocessing import Process

#parameters list: pin, count, brightness
eyes_leds = (board.D21, 1, 1) # two eyes in parallel
mouth_leds = (board.D18, 18, 0.5)

strips = {
    'EYES': eyes_leds,
    'MOUTH': mouth_leds
}

pin = None
pixels = None

ORDER = neopixel.GRB

default_color = (243, 253, 0)
no_color = (0, 0, 0)
orange = (255,165,0)
darkorange = (255,140,0)
blue = (0,0,255)
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

is_talking = False

def fill_pixels(pixels, color):
    pixels.fill(color)
    pixels.show()

def blink(pixels, pin, mode, timeout = 30):
    if pin != board.D21:
        print('Teeth do not support blink command!')
        return

    if mode == 'plugged_in':
        phase_1_color = darkorange
        phase_2_color = blue
        period = 0.1
    else:
        phase_1_color = no_color
        phase_2_color = default_color
        period = 0.25

    t = 0
    while t < timeout:  # maximum answer length to prevent infinite loop
        pixels.fill(phase_1_color)
        pixels.show()
        time.sleep(period)
        pixels.fill(phase_2_color)
        pixels.show()
        time.sleep(period)
    t += period * 4

def talk(pixels, pin, mode, timeout = 30):
    if pin != board.D18:
        print('Eyes do not support talk command!')
        return

    if mode == 'plugged_in':
        back_color = darkorange
        front_color = blue
        period = 0.1
    else:
        back_color = no_color
        front_color = default_color
        period = 0.25

    t = 0
    while t < timeout: # maximum answer length to prevent infinite loop
        fill_range(pixels, pin, 6, 12, front_color, back_color)
        time.sleep(period)

        fill_range(pixels, pin, 2, 4, front_color, back_color)
        fill_range(pixels, pin, 6, 8, front_color)
        fill_range(pixels, pin, 10, 12, front_color)
        fill_range(pixels, pin, 14, 16, front_color)
        time.sleep(period)

        fill_range(pixels, pin, 6, 12, front_color, back_color)
        time.sleep(period)

        fill_range(pixels, pin, 1, 5, front_color, back_color)
        fill_range(pixels, pin, 6, 7, front_color)
        fill_range(pixels, pin, 11, 12, front_color)
        fill_range(pixels, pin, 13, 17, front_color)
        time.sleep(period)
        t += period * 4

def fill_range(pixels, pin, start, end, front_color, back_color = None):
    if pin != board.D18:
        print('Eyes do not support talk command!')
        return

    if back_color:
        pixels.fill(back_color)
    for i in range(start, end):
        pixels[i] = front_color
    pixels.show()

def sin_cos_graph(pixels, pin, func, front_color, back_color):
    if pin != board.D18:
        print('Eyes do not support talk command!')
        return
    if func != math.sin and func != math.cos:
        print('Only sin() and cos() are supported!')
        return
    pixels.fill(back_color)
    t = 0
    for x in range(0, 6):
        y = func(t)
        j = x
        if y >= -1 and y < -0.33:
            i = 0
        elif y >= -0.33 and y < 0.33:
            i = 1
            j = revert_row1[x]
        else:
            i = 2
        c = i * 6 + j
        pixels[c] = front_color
        t += 1.57
    pixels.show()

class BacklightControl:
    def __init__(self, strip):
        self.pixels = None
        if strip in strips:
            self.__init_pixels(strips[strip])
        else:
            print("Strip not found!")
        self.backlight_commands = {
            'ON': lambda: fill_pixels(self.pixels, default_color),
            'OFF': lambda: fill_pixels(self.pixels, no_color),
            'TALK': lambda: talk(self.pixels, self.pin, 'normal'),
            'PLUGGED_IN': lambda: talk(self.pixels, self.pin, 'plugged_in'),
            'BLINK_NORMAL': lambda: blink(self.pixels, self.pin, 'normal'),
            'BLINK_PLUGGED_IN': lambda: blink(self.pixels, self.pin, 'plugged_in')
        }

    def __del__(self):
        self.pixels.deinit()

    def exec_cmd(self, command, delay = None):
        if delay:
            time.sleep(delay)
        if command in self.backlight_commands:
            func = self.backlight_commands[command]
            p = Process(target=func, args=())
            p.start()
            return p

    def __init_pixels(self, leds):
        self.pin = leds[0]
        self.pixels = neopixel.NeoPixel(leds[0], leds[1], brightness=leds[2], auto_write=False,
                                   pixel_order=ORDER)
