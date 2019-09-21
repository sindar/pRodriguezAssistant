import board
import neopixel
import sys
import getopt

eyes_pin = board.D21
teeth_pin = board.D18

eyes_num = 1 # two eyes in parallel
teeth_num = 18

ORDER = neopixel.GRB

def switch_pixels(pixels, on):
    if on:
        pixels.fill((243, 253, 0))
    else:
        pixels.fill((0, 0, 0))
    pixels.show()

def main(argv):
    #print ('Argument List:', str(sys.argv))
    pixels = None
    on = False
    try:
        opts, args = getopt.getopt(argv, "hl:s:", ["light=", "switch="])
    except getopt.GetoptError:
        print ('backlight.py -l <eyes|teeth> -s <on|off>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('backlight.py -l <eyes|teeth> -s <on|off>')
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
    if (pixels):
        switch_pixels(pixels, on)

if __name__ == "__main__":
   main(sys.argv[1:])