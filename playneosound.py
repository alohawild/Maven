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
    Adafruit for all the good ideas! A lot of the equilizer math code comes
    from an example program. Here are their credits for MIT licenses.
    Copyright (c) 2017 Dan Halbert for Adafruit Industries
    Copyright (c) 2017 Kattni Rembor, Tony DiCola for Adafruit Industries

==============================================================================
This program drives NeoPixels for circuit playground using brightness as 
an equilizer. I also added a cool restart look.

"""
__author__ = "michaelwild"
__copyright__ = "Copyright (C) 2018 Michael Wild"
__license__ = "Apache License, Version 2.0"
__version__ = "0.1.0"
__credits__ = ["Michael Wild", "Adafruit.com"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"

import random
import board
import neopixel
import time
import array
import math
import audiobusio
import digitalio

# ###############################################################
# Exponential scaling factor.
# Should probably be in range -10 .. 10 to be reasonable.
SCALE_EXPONENT = math.pow(10, 2 * -0.1)

NUM_VALUES = 9

# Number of samples to read at once.
NUM_SAMPLES = 160

def constrain(value, floor, ceiling):
    """
    Restrict value to be between floor and ceiling.
    """
    return max(floor, min(value, ceiling))

def log_scale(input_value, input_min, input_max, output_min, output_max):
    """
    Scale input_value between output_min and output_max, exponentially.
    Note: Division is unprotected! input_max must not be same as input_min!
    """
    normalized_input_value = (input_value - input_min) / \
                             (input_max - input_min)
    return output_min + \
        math.pow(normalized_input_value, SCALE_EXPONENT) \
        * (output_max - output_min)

def normalized_rms(values):
    """
    Remove DC bias before computing RMS.
    Note: Empty list will cause this to fail!
    """
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )
    return math.sqrt(samples_sum / len(values))

def mean(values):
    """
    Compute the mean
    Note: Empty list will cause this to fail!
    """
    return sum(values) / len(values)

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
######################################################
pixel_count = 10  # Number of pixels in your strip

color_change = 16  # Number to increase color change (how fast you want it)

pixels = neopixel.NeoPixel(board.NEOPIXEL, pixel_count, brightness=0.1)
pixels.fill((0, 0, 0))
pixels.show()
######################################################
# LED setup
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
led.value = False

######################### Start up ##############################
print("Neopixel Wheel and Equilizer")
print(__version__, " ", __copyright__, " ", __license__)

print("Start")

# Listening definition
mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)

# Record an initial sample to calibrate. Assume it's quiet when we start.
samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))
# Force floor
input_floor = 50

# Corresponds to sensitivity: lower means brighter light up with lower sound
input_ceiling = input_floor + 500

peak = 0

# ######################## MAIN LOOP ##############################
spin = 0
while True:
    
    # Reset wheel every zero
    if (spin == 0):
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(1.0) # Just for the coolness to have it stop and freeze
        print("Running")  # Just a note to tell us everything is good
        colors = [random.randint(0, 255) for x in range(0, pixel_count)]
        for x in range(0, (pixel_count)):
            pixels[x] = wheel(colors[x])
            pixels.show()
    
    # so spin wheel
    newcolors = []
    for x in range(0, pixel_count):
        nc = (colors[x] + color_change) % 256
        pixels[x] = wheel(nc)
        pixels.show()
        newcolors.append(nc)
    colors = newcolors.copy()
    
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    
    # Compute scaled logarithmic reading in the range 0 to NUM_PIXELS
    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_VALUES)
                  
    pixels.brightness = (c/10.0) + 0.1 # Turn value into brightness values
    
    # On sound turn on LED

    if (c == 0 ):
        led.value = False
    else:
        led.value = True
    
    spin = (spin + 1) % 256  # run from 0 to 255