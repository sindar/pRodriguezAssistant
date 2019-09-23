import board
import neopixel
import sys
import getopt

eyes_pin = board.D21
teeth_pin = board.D18

eyes_num = 1 # two eyes in parallel
teeth_num = 18

ORDER = neopixel.GRB

def switch_pixels(pixels, on, color):
    if on:
        pixels.fill(color)
    else:
        pixels.fill((0, 0, 0))
    pixels.show()

def main(argv):
    #print ('Argument List:', str(sys.argv))
    pixels = None
    on = False
    red = 243
    green = 253
    blue = 0
    if len(argv) < 2:
        print ('backlight.py -l <eyes|teeth> -s <on|off> -r <val> -g <val> -b <val>')
    try:
        opts, args = getopt.getopt(argv, "hl:s:r:g:b:", ["light=", "switch=", "red=", "green=", "blue="])
    except getopt.GetoptError:
        print ('backlight.py -l <eyes|teeth> -s <on|off> -r <val> -g <val> -b <val>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('backlight.py -l <eyes|teeth> -s <on|off> -r <val> -g <val> -b <val>')
            sys.exit()
        elif opt in ("-l", "--light"):
            if (arg == 'eyes'):
                pixels = neopixel.NeoPixel(eyes_pin, eyes_num, brightness=0.2, auto_write=False,
                                pixel_order=ORDER)
            else:
                pixels = neopixel.NeoPixel(teeth_pin, teeth_num, brightness=0.1, auto_write=False,
                                     pixel_order=ORDER)
        elif opt in ("-s", "--switch"):
            if (arg == 'on'):
                on = True
            else:
                on = False
        elif opt in ("-r", "--red"):
            red = int(arg)
        elif opt in ("-g", "--green"):
            green = int(arg)
        elif opt in ("-b", "--blue"):
            blue = int(arg)

    if (pixels):
        switch_pixels(pixels, on, (red, green, blue))

if __name__ == "__main__":
   main(sys.argv[1:])