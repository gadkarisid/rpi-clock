#!/usr/bin/python

# This script draws '----' and then clears the display of all data.

import time
import datetime
from Adafruit_7Segment import SevenSegment

display = SevenSegment(address=0x70)

# Clear display
display.disp.clear()
display.writeDigitRaw(0, 64)
display.writeDigitRaw(1, 64)
display.writeDigitRaw(3, 64)
display.writeDigitRaw(4, 64)
time.sleep(1)
display.disp.clear()
