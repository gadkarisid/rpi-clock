#!/usr/bin/python

# Test script to make sure display is functioning correctly and all segments work.

import time
from Adafruit_7Segment import *

# Initialize display
display = SevenSegment(address=0x70)

# Set brightness
brightness = 15
LEDBackpack().setBrightness(brightness)

# Clear display
display.disp.clear()

# Light all segments individually
position = 0 
while (position <= 4): 
	display.writeDigitRaw(position,(1))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2+4))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2+4+8))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2+4+8+16))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2+4+8+16+32))
        time.sleep(.12)
        display.writeDigitRaw(position,(1+2+4+8+16+32+64))
        time.sleep(.12)
        position += 1
        if (position == 2):
                position = 3
display.writeDigitRaw(2,2)
time.sleep(1)
display.disp.clear()
