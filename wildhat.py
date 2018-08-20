"""
    Copyright 2018 by Michael Wild (alohawild)

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
    Note:
    Some of the code is harvested and rewritten from Adafruit. Thank you
    Adafruit for all the good ideas!

==============================================================================
This program drives NeoPixels

"""
__author__ = "michaelwild"
__copyright__ = "Copyright (C) 2018 Michael Wild"
__license__ = "Apache License, Version 2.0"
__version__ = "0.0.4"
__credits__ = ["Michael Wild", "Adafruit.com"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"

import random
import board
import neopixel
import adafruit_dotstar as dotstar
from touchio import TouchIn
from analogio import AnalogIn

# ######################## Definitions ##############################
pixel_pin = board.D1  # The pin the NeoPixels are connected to

pixel_count = 4  # Number of pixels in your strip

color_change = 16  # Number to increase color change (how fast you want it)

pixels = neopixel.NeoPixel(pixel_pin, pixel_count,
                           brightness=.4, auto_write=False)
                           
# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=1.0)

# Capacitive touch on A1
touch1 = TouchIn(board.A1)

# Analog input on A2
analog1in = AnalogIn(board.A2)

def wheel(pos):
    """
    pos: place on color wheel of 0-255 values
    Helper to give us a nice color swirl
    Thank you Adafruit for the nice wheel routine!
    
    Input a value 0 to 255 to get a color value.
    The colours are a transition r - g - b - back to r.
    """
    if (pos < 0):
        return [0, 0, 0]
    if (pos > 255):
        return [0, 0, 0]
    if (pos < 85):
        return [int(pos * 3), int(255 - (pos*3)), 0]
    elif (pos < 170):
        pos -= 85
        return [int(255 - pos*3), 0, int(pos*3)]
    else:
        pos -= 170
        return [0, int(pos*3), int(255 - pos*3)]
        
# Helper to convert analog input to voltage
def getVoltage(pin):
    """
    Another great routine from Adafruit
    """
    
    return ((pin.value * 3.3) / 65536 - 1.67)*100
    
# ######################## Start up ##############################
print("Wild Light Hat")
print(__version__, " ", __copyright__, " ", __license__)

print("Start")

# Randomly assign colors using wheel
colors = [random.randint(0, 255) for x in range(0, pixel_count)]
for x in range(0, (pixel_count)):
    pixels[x] = wheel(colors[x])
    pixels.show()

# ######################## MAIN LOOP ##############################

spin = 0
flashvalue = 0
flash = False
while True:
    # spin internal LED around!
    # This is a cool idea from Adafruit to make it look like the dot runs
    # by itself!
    dot[0] = wheel(spin)
    dot.show()
    
    # use A1 as capacitive touch to turn on internal LED
    if touch1.value:
        print("A1 touched!")
        # Randomly assign colors using wheel
        for x in range(0, (pixel_count)):
            pixels[x] = wheel(0)
            pixels.show()
        colors = [random.randint(0, 255) for x in range(0, pixel_count)]
    
    soundcheck = getVoltage(analog1in)
    if soundcheck > 5.0:
        flash = True
        print("A1: %0.2f" % soundcheck)
        # Normalise data a bit 
        if soundcheck < 6:
            flashvalue = 0
        elif soundcheck < 13.0:
            flashvalue = 1
        elif soundcheck < 25:
            flashvalue = 2
        elif soundcheck < 50:
            flashvalue = 3
        elif soundcheck < 75:
            flashvalue = 4
        else:
            flashvalue = 5
        print("Sound value: ", flashvalue)
    else:
        flash = False

    # so spin wheel
    if spin == 0:
        newcolors = []
        for x in range(0, pixel_count):
            nc = (colors[x] + color_change) % 256
            pixels[x] = wheel(nc)
            pixels.show()
            newcolors.append(nc)
        colors = newcolors.copy()
    
    # flash for sound
    if flash:
        pixel_flash = int(((pixel_count - 1) / 5.0) * flashvalue)
        pixels[pixel_flash] = wheel(128)
        colors[pixel_flash] = 128
        pixels.show()
        print("Flash!!!!!!!!", pixel_flash)
        
    spin = (spin + 1) % 256  # run from 0 to 255