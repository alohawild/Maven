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
__version__ = "0.0.1"
__credits__ = ["Michael Wild", "Adafruit.com"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"

import random
import board
import neopixel
import adafruit_dotstar as dotstar

# ######################## Definitions ##############################
pixel_pin = board.D2  # The pin the NeoPixels are connected to

pixel_count = 30  # Number of pixels in your strip

color_change = 16  # Number to increase color change (how fast you want it)

pixels = neopixel.NeoPixel(pixel_pin, pixel_count,
                           brightness=.4, auto_write=False)
                           
# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2) 

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

# ######################## Start up ##############################
print("Neopixel Wheel random")
print(__version__, " ", __copyright__, " ", __license__)

print("Start")

# ######################## MAIN LOOP ##############################
i = 0
while True:
    # spin internal LED around!
    # This is a cool idea from Adafruit to make it look like the dot runs
    # by itself!
    dot[0] = wheel(i)
    dot.show()
    
    # shoot color
    color = random.randint(0, 255)
    pixels[0] = wheel(color)
    for x in range(1, pixel_count):
        pixels[x-1] = [0,0,0]
        pixels[x] = wheel(color)
        pixels.show()
        
    i = (i+1) % 256  # run from 0 to 255