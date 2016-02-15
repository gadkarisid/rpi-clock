# Copyright (c) 2015-2016 Sid Gadkari. All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Last Revision Date: 02/16/2016

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
