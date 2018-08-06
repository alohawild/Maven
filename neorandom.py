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
__version__ = "1.0.0"
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

pixel_count = 15  # Number of pixels in your strip

pixels = neopixel.NeoPixel(pixel_pin, pixel_count,
                           brightness=.4, auto_write=False)
                           
# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2) 

# Colors:
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
# Extra:
GOLD = (255, 222, 30)
PINK = (242, 90, 255)
AQUA = (50, 255, 255)
JADE = (0, 255, 40)
AMBER = (255, 100, 0)

colors = (RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA, WHITE)

colorswithsparkle = (GOLD, PINK, AQUA, JADE, AMBER)

def sparkle():
    """
    This routine just updates a random neopixel to sparkle using some 
    nice bright colors.
    """
    # Random color and assign to random pixel
    c = random.randint(0, (len(colorswithsparkle) - 1))
    (red_value, green_value, blue_value) = colorswithsparkle[c]
    p = random.randint(0, (pixel_count-1))
    pixels[p] = (red_value, green_value, blue_value)
    pixels.show()
    pixels[p] = (red_value // 2, green_value // 2, blue_value // 2)
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
print("Neopixel Random")
print(__version__, " ", __copyright__, " ", __license__)

print("Start")

# ######################## MAIN LOOP ##############################
i = 0
j = 0
while True:
    # spin internal LED around!
    # This is a cool idea from Adafruit to make it look like the dot runs
    # by itself!
    dot[0] = wheel(i)
    dot.show()
    
    # so the neopixels run at a different speed of the dot. Just for looks!
    if j == 0:
        p = random.randint(0, (pixel_count-1))
        c = random.randint(0, (len(colors) - 1))
        pixels[p] = colors[c]
        sparkle()
        
    i = (i+1) % 256  # run from 0 to 256
    j = (j+1) % 64  # run a short time