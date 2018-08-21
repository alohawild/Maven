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
This program drives NeoPixels for circuit playground. 

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

# ######################## Definitions #############################

pixel_count = 10  # Number of pixels in your strip

color_change = 16  # Number to increase color change (how fast you want it)

pixels = neopixel.NeoPixel(board.NEOPIXEL, pixel_count, brightness=0.2)
pixels.fill((0, 0, 0))
pixels.show()

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

# Randomly assign colors using wheel
colors = [random.randint(0, 255) for x in range(0, pixel_count)]
for x in range(0, (pixel_count)):
    pixels[x] = wheel(colors[x])
    pixels.show()

# ######################## MAIN LOOP ##############################
i = 0
while True:
    
    # so spin wheel
    newcolors = []
    for x in range(0, pixel_count):
        nc = (colors[x] + color_change) % 256
        pixels[x] = wheel(nc)
        pixels.show()
        newcolors.append(nc)
    colors = newcolors.copy()
        
    i = (i+1) % 256  # run from 0 to 255