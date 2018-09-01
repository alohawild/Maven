
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
    I have harvested Sparkfun code too. Their code is C for Arduino. 

From:  

https://learn.sparkfun.com/tutorials/avr-based-serial-enabled-lcds-hookup-guide/
i2c-hardware-hookup--example-code---basic

 To get this code to work, attached an OpenLCD to an Arduino Uno using the 
 following pins:
 SCL (OpenLCD) to A5 (Arduino)
 SDA to A4
 VIN to 5V
 GND to GND
 Command cheat sheet:
 ASCII / DEC / HEX
 '|'    / 124 / 0x7C - Put into setting mode
 Ctrl+c / 3 / 0x03 - Change width to 20
 Ctrl+d / 4 / 0x04 - Change width to 16
 Ctrl+e / 5 / 0x05 - Change lines to 4
 Ctrl+f / 6 / 0x06 - Change lines to 2
 Ctrl+g / 7 / 0x07 - Change lines to 1
 Ctrl+h / 8 / 0x08 - Software reset of the system
 Ctrl+i / 9 / 0x09 - Enable/disable splash screen
 Ctrl+j / 10 / 0x0A - Save currently displayed text as splash
 Ctrl+k / 11 / 0x0B - Change baud to 2400bps
 Ctrl+l / 12 / 0x0C - Change baud to 4800bps
 Ctrl+m / 13 / 0x0D - Change baud to 9600bps
 Ctrl+n / 14 / 0x0E - Change baud to 14400bps
 Ctrl+o / 15 / 0x0F - Change baud to 19200bps
 Ctrl+p / 16 / 0x10 - Change baud to 38400bps
 Ctrl+q / 17 / 0x11 - Change baud to 57600bps
 Ctrl+r / 18 / 0x12 - Change baud to 115200bps
 Ctrl+s / 19 / 0x13 - Change baud to 230400bps
 Ctrl+t / 20 / 0x14 - Change baud to 460800bps
 Ctrl+u / 21 / 0x15 - Change baud to 921600bps
 Ctrl+v / 22 / 0x16 - Change baud to 1000000bps
 Ctrl+w / 23 / 0x17 - Change baud to 1200bps
 Ctrl+x / 24 / 0x18 - Change the contrast. Follow Ctrl+x with number 0 to 
 255. 120 is default.
 Ctrl+y / 25 / 0x19 - Change the TWI address. Follow Ctrl+x with number 0 
 to 255. 114 (0x72) is default.
 Ctrl+z / 26 / 0x1A - Enable/disable ignore RX pin on startup 
 (ignore emergency reset)
 '-'    / 45 / 0x2D - Clear display. Move cursor to home position.
        / 128-157 / 0x80-0x9D - Set the primary backlight brightness. 
        128 = Off, 157 = 100%.
        / 158-187 / 0x9E-0xBB - Set the green backlight brightness. 158 = Off,
        187 = 100%.
        / 188-217 / 0xBC-0xD9 - Set the blue backlight brightness. 188 = Off,
        217 = 100%.
 For example, to change the baud rate to 115200 send 124 followed by 18.



==============================================================================
Run Sparkfun cool 3.3V LCD using python

"""
__author__ = "michaelwild"
__copyright__ = "Copyright (C) 2018 Michael Wild"
__license__ = "Apache License, Version 2.0"
__version__ = "0.1.0"
__credits__ = ["Michael Wild", "Sparkfun.com", "Adafruit.com"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"

import busio
import digitalio
import board
import time
import microcontroller

# LED setup
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# ######################## Start up ##############################

print("LCD Test Program: Playground Express")
print(__version__, " ", __copyright__, " ", __license__)

print("Start")

print("Access I2C Bus")
while not i2c.try_lock():
    pass
print("I2C addresses found:", [hex(device_address) 
                               for device_address in i2c.scan()])
time.sleep(2)

print("Running!")

# We use a "spin" controller to split up the loop. So on every spin==0 we do 
# something interesting
# On other values we might do maintenance or change a value or detect a change.
spin = 0
contrast = 0

# Clear display
i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)

# Back light to full power: Green!
i2c.writeto(0x72, bytes([0x7C, 0xBB]), stop=False)

# This is the infinite loop that runs the process. Break out to end control 
# and return to REPL
while True:
    
    temp = microcontroller.cpu.temperature * (9.0 / 5.0) + 32  # Get temp always
    
    if (spin == 0):
        i2c.writeto(0x72, bytes([0x7C, 0x18, contrast]), stop=False)
        time.sleep(0.5)

        i2c.writeto(0x72, bytes([0x7C, 0x2D]), stop=False)  # Clear LCD
        time.sleep(0.5)
        data = "CPU Temp: %d\n" % (temp)
        i2c.writeto(0x72, data, stop=False)
        time.sleep(0.5)
        
        # Run LED to blink as we update display (just cool to know that we did 
        # something)
        if (led.value):
            led.value = False
        else:
            led.value = True
            
        contrast = (contrast + 1) % 256  # run from 0 to 255
        time.sleep(0.5)
    
    spin = (spin + 1) % 256  # run from 0 to 255

    