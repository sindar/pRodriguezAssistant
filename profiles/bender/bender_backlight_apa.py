# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import profiles.bender.apa102 as apa102
import time
import math
from multiprocessing import Process

# #parameters list: pin, count, brightness
# eyes_leds = (board.D21, 1, 1) # two eyes in parallel
# mouth_leds = (board.D18, 18, 0.5)

# strips = {
#     'EYES': eyes_leds,
#     'MOUTH': mouth_leds
# }

# pin = None
# pixels = None

# ORDER = neopixel.GRB

default_color = (243, 253, 0)
no_color = (0, 0, 0)
orange = (255,165,0)
darkorange = (255,140,0)
blue = (0,0,255)
red = (255,0,0)
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

is_talking = False

NUM_LED = 3
dev = apa102.APA102(num_led=NUM_LED)

def fill_pixels(color):
    for i in range(NUM_LED):
        dev.set_pixel(i, color[0], color[1], color[2])
    dev.show()


def blink(mode, timeout = 300):
    period = 0.25
    t = 0
    while t < timeout:  # maximum answer length to prevent infinite loop
        fill_pixels(default_color)
        time.sleep(period)
        fill_pixels(no_color)
        time.sleep(period)
    t += period * 4

def talk(mode, timeout = 300):
    blink(mode)

class BacklightControl:
    def __init__(self, strip):
        global red
        self.pixels = None
        # if strip in strips:
        #     self.__init_pixels(strips[strip])
        # else:
        #     print("Strip not found!")
        self.backlight_commands = {
            'ON': lambda: fill_pixels(default_color),
            'OFF': lambda: fill_pixels(no_color),
            'TALK': lambda: talk('normal'),
            'XMAS': lambda: talk('xmas'),
            'EYES XMAS': lambda: fill_pixels(red),
            'PLUGGED_IN': lambda: talk('plugged_in'),
            'BLINK_NORMAL': lambda: blink('normal'),
            'BLINK_PLUGGED_IN': lambda: blink('plugged_in')
        }

    # def __del__(self):
    #     self.pixels.deinit()

    def exec_cmd(self, command, delay = None):
        if delay:
            time.sleep(delay)
        if command in self.backlight_commands:
            func = self.backlight_commands[command]
            p = Process(target=func, args=())
            p.start()
            return p

    # def __init_pixels(self, leds):
        # self.pin = leds[0]
        # self.pixels = neopixel.NeoPixel(leds[0], leds[1], brightness=leds[2], auto_write=False,
        #                            pixel_order=ORDER)
