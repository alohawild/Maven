
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
import microcontroller
import busio
import adafruit_gps
from analogio import AnalogOut
from touchio import TouchIn

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

pixel_count = 10  # Number of pixels in your strip
color_change = 32  # Number to increase color change (how fast you want it)
pixels = neopixel.NeoPixel(board.NEOPIXEL, pixel_count, brightness=0.1)
pixels.fill((0, 0, 0))
pixels.show()

i2c = busio.I2C(board.SCL, board.SDA)

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=3000)

# Analog output on A0
aout = AnalogOut(board.A0)

# Capacitive touch on A3
touch = TouchIn(board.A3)

print("Amazing Fez")
print(__version__, " ", __copyright__, " ", __license__)

print("Access I2C Bus")
while not i2c.try_lock():
    pass
time.sleep(2)

print("GPS set-up")
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)

gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

gps.send_command(b'PMTK220,1000')

mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)

samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))
input_floor = 50

input_ceiling = input_floor + 500

peak = 0

# Clear display
i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)
# Back light to full power: Green!
i2c.writeto(0x72, bytes([0x7C, 0xBB]), stop=False)
# Contrast to full power
i2c.writeto(0x72, bytes([0x7C, 0x18, 0x00]), stop=False)
time.sleep(1.0)

spin = 0
refreshtemp = True
# Call about once a second
last_print = time.monotonic()
havefix = False
refreshGPS = True
oldtemp = -9999.99
banner = ""

while True:

    if touch.value:
        spin = 0
    
    tempmicro = microcontroller.cpu.temperature * (9.0 / 5.0) + 32  # Get temp
    
    sat = 0
    if gps.satellites is not None:
        sat = gps.satellites
        if sat > 6:
            sat = 6
        aout.value = int(49151 + 16384 * (sat / 6.0))
    else:
        aout.value = 0
    
    current = time.monotonic()
    if current - last_print >= 0.50:
        last_print = current
        gps.update()  # Update GPS
    
    if (havefix != gps.has_fix):
        refreshGPS = True
        havefix = gps.has_fix
        
    if abs(tempmicro - oldtemp) > 1.5:
        spin = 0
        oldtemp = tempmicro
    
    # Reset wheel every zero
    if (spin == 0):
        pixels.fill((0, 0, 0))
        pixels.show()
        i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=True)
        time.sleep(1.0)  # Just for the coolness to have it stop and freeze
        colors = [random.randint(0, 255) for x in range(0, pixel_count)]
        for x in range(0, (pixel_count)):
            pixels[x] = wheel(colors[x])
            pixels.show()
        banner = "The Amazing Fez "
        refreshGPS = True
        
    if (refreshGPS):

        if gps.has_fix:
            banner = banner + ' Lat: {0:.2f} '.format(gps.longitude) + \
                ' Long: {0:.2f} '.format(gps.latitude)
            if gps.altitude_m is not None:
                banner = banner + ' Altitude: {} meters '.\
                    format(gps.altitude_m)

        refreshGPS = False
 
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

    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_VALUES)
    pixels.brightness = (c/10.0) + 0.1  # Turn value into brightness values
    
    tempmicro = microcontroller.cpu.temperature * (9.0 / 5.0) + 32  # Get temp
    
    if (refreshtemp):
        data = ' CPU Temp: {0:.2f} '.format(tempmicro)
        banner = banner + data
        refreshtemp = False

    i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)
    if (len(banner) > 32):
        data = banner[0:31]
        i2c.writeto(0x72, data, stop=True)
        time.sleep(0.3)
        banner = banner[1:]
    elif (len(banner) > 0):
        i2c.writeto(0x72, banner, stop=True)
        time.sleep(0.3)
        refreshtemp = True
        refreshGPS = True

    spin = (spin + 1) % 256  # run from 0 to 255