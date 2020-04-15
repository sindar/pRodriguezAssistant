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
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

is_talking = False

def fill_pixels(pixels, color):
    pixels.fill(color)
    pixels.show()

def talk(pixels, pin):
    if pin != board.D18:
        print('Eyes do not support talk command!')
        return
    i = 0
    while i < 30: # maximum answer length to prevent infinite loop
        pixels.fill((0, 0, 0))
        for i in range(6, 12):
            pixels[i] = default_color
        pixels.show()
        time.sleep(0.25)

        sin_cos_graph(pixels, pin, math.cos)
        time.sleep(0.25)

        pixels.fill((0, 0, 0))
        for i in range(6, 12):
            pixels[i] = default_color
        pixels.show()
        time.sleep(0.25)

        sin_cos_graph(pixels, pin, math.sin)
        time.sleep(0.25)

def sin_cos_graph(pixels, pin, func):
    if pin != board.D18:
        print('Eyes do not support talk command!')
        return
    if func != math.sin and func != math.cos:
        print('Only sin() and cos() are supported!')
        return
    pixels.fill((0, 0, 0))
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
        pixels[c] = default_color
        t += 1.57
    pixels.show()

class BacklightControl:
    backlight_enabled = True

    def __init__(self, strip):
        self.pixels = None
        if strip in strips:
            self.__init_pixels(strips[strip])
        else:
            print("Strip not found!")
        self.backlight_commands = {
            'ON': lambda: fill_pixels(self.pixels, default_color),
            'OFF': lambda: fill_pixels(self.pixels, no_color),
            'TALK': lambda: talk(self.pixels, self.pin)
        }

    def exec_cmd(self, command):
        if command in self.backlight_commands:
            func = self.backlight_commands[command]
            p = Process(target=func, args=())
            p.start()
            return p

    def __init_pixels(self, leds):
        self.pin = leds[0]
        self.pixels = neopixel.NeoPixel(leds[0], leds[1], brightness=leds[2], auto_write=False,
                                   pixel_order=ORDER)
