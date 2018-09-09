"""

==============================================================================
This is the "Amazing Fez" project. Comments removed for space.

"""
__author__ = "michaelwild"
__copyright__ = "Copyright (C) 2018 Michael Wild"
__license__ = "Apache License, Version 2.0"
__version__ = "0.3.0"
__credits__ = ["Michael Wild", "Adafruit.com", "Sparkfun.com"]
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
import microcontroller
import busio
import adafruit_gps
from analogio import AnalogOut
from touchio import TouchIn

# ###############################################################
# Exponential scaling factor.
# Should probably be in range -10 .. 10 to be reasonable.
SCALE_EXPONENT = math.pow(10, 2 * -0.1)

NUM_VALUES = 9

# Number of samples to read at once.
NUM_SAMPLES = 160

def constrain(value, floor, ceiling):

    return max(floor, min(value, ceiling))

def log_scale(input_value, input_min, input_max, output_min, output_max):

    normalized_input_value = (input_value - input_min) / \
                             (input_max - input_min)
    return output_min + \
        math.pow(normalized_input_value, SCALE_EXPONENT) \
        * (output_max - output_min)

def normalized_rms(values):

    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )
    return math.sqrt(samples_sum / len(values))

def mean(values):

    return sum(values) / len(values)

def wheel(pos):

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
color_change = 32  # Number to increase color change (how fast you want it)
pixels = neopixel.NeoPixel(board.NEOPIXEL, pixel_count, brightness=0.1)
pixels.fill((0, 0, 0))
pixels.show()
######################################################
# LED setup
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
led.value = False
######################################################
# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
######################################################
# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=3000)
######################################################
# Analog output on A0
aout = AnalogOut(board.A0)
#######################################################
# Capacitive touch on A3
touch = TouchIn(board.A3)
#######################################################
print("Amazing Fez")
print(__version__, " ", __copyright__, " ", __license__)

print("Access I2C Bus")
while not i2c.try_lock():
    pass
print("I2C addresses found:", [hex(device_address) 
                               for device_address in i2c.scan()])
time.sleep(2)

print("GPS set-up")
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)
# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b'PMTK220,1000')

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

# Clear display
i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)
# Back light to full power: Green!
i2c.writeto(0x72, bytes([0x7C, 0xBB]), stop=False)
# Contrast to full power
i2c.writeto(0x72, bytes([0x7C, 0x18, 0x00]), stop=False)
time.sleep(1.0)
data = "Starting!"
i2c.writeto(0x72, data, stop=True)
time.sleep(1.0)
# ######################## MAIN LOOP ##############################
spin = 0
# Call about once a second
last_print = time.monotonic()
havefix = False
refreshLCD = True
oldtemp = -9999.99
while True:
    
    # use A3 as capacitive touch to turn on internal LED
    if touch.value:
        spin = 0
    
    tempmicro = microcontroller.cpu.temperature * (9.0 / 5.0) + 32  # Get temp
    
    # set analog output to 0-3.3V (0-65535 in increments)
    aout.value = int(65535 - (spin * 256)/2)
    
    current = time.monotonic()
    if current - last_print >= 0.50:
        last_print = current
        gps.update()  # Update GPS
    
    # reset if fix changed
    if (havefix != gps.has_fix):
        spin = 0
        havefix = gps.has_fix
        
    # reset if temp changes degree
    if abs(tempmicro - oldtemp) > 1.5:
        spin = 0
        oldtemp = tempmicro
    
    # Reset wheel every zero
    if (spin == 0):
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(1.0)  # Just for the coolness to have it stop and freeze
        print("Running")  # Just a note to tell us everything is good
        colors = [random.randint(0, 255) for x in range(0, pixel_count)]
        for x in range(0, (pixel_count)):
            pixels[x] = wheel(colors[x])
            pixels.show()
        refreshLCD = True
        
    if (refreshLCD):
        # print temp of CPU
        i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)
        data = 'CPU Temp: {0:.2f} '.format(tempmicro)
        if gps.has_fix:
            moredata = '{0:.2f}'.format(gps.longitude)
            evenmore = ' {0:.2f}'.format(gps.latitude)
            data = data + moredata + evenmore
        i2c.writeto(0x72, data, stop=True)
        refreshLCD = False
    
    # so spin wheel
    newcolors = []
    for x in range(0, pixel_count):
        nc = (colors[x] + random.randint(1, color_change)) % 256
        pixels[x] = wheel(nc)
        pixels.show()
        newcolors.append(nc)
    colors = newcolors.copy()
    
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    # Compute scaled logarithmic reading in the range 0 to NUM_PIXELS
    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_VALUES)
    pixels.brightness = (c/10.0) + 0.1  # Turn value into brightness values
    
    # On sound turn on LED on sound
    if (c == 0):
        led.value = False
    else:
        led.value = True

    spin = (spin + 1) % 256  # run from 0 to 255