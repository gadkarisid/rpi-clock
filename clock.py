# Copyright (c) 2015-2016 Sid Gadkari. All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Last Revision Date: 02/22/2016

#!/usr/bin/python
import os
import time
import datetime
import signal
import sys
from Adafruit_7Segment import *


#---------------------BEGIN USER PREFERENCES---------------------
# Define time format (12 or 24 hour)
hour_format = 24

# Define if you want to see weather information (yes/no)
show_weather = "yes"

# Define temperature unit (F or C)
unit_pref = "F"

# Define your zip code for weather updates
user_zipcode = 123456

# Default display brightness (0 to 15)
default_brightness = 15

# Auto dimming based on time of day (enabled/disabled)
auto_dimming = "enabled"

# Display brightness during day (0 to 15)
day_bright = 9

# Display brightness during night (0 to 15)
night_bright = 5
#----------------------END USER PREFERENCES----------------------


# Initialize display
display = SevenSegment(address=0x70)
LEDBackpack().setBrightness(default_brightness)

# Change working directory
os.chdir('/usr/bin/rpi-clock')

# Set the hour offset based on user preference
hour_offset = 24 - hour_format
# Set numeric zip code to a string value
zipcode = str(user_zipcode)

# Define system signal handler function
def signal_handler(signal, frame):
	display.disp.clear()
	sys.exit(0)

# Define current time function
def currenttime():
	global now
	global hour
	global minute
	global second

	# Get current time
	now = datetime.datetime.now()
	hour = now.hour
	minute = now.minute
	second = now.second

	# If the current hour is greater than 12, reformat the hour to conform to the user preference setting
	if (hour > 12):
		hour = (now.hour - hour_offset)
	
# Define weather update function
def weatherupdate():
	global raw_temp
	global current_temp
	global unit_pref
	global weather_update_error
	
	# Set weather_update_error to default value
	weather_update_error = "false"
		
	# Create URL for weather lookup
	url = "http://www.wunderground.com/cgi-bin/findweather/getForecast?query=" + zipcode
	# Create wget command to pull weather info
	weatherupdate = "wget -T 15 -t 1 -O weatherdata.tmp " + url
				
	# Get current weather
	os.system(weatherupdate)
		
	# Read weatherdata.tmp file and extract current temperature
	if os.path.isfile('weatherdata.tmp'):
		if os.path.getsize('weatherdata.tmp') > 0:
			with open('weatherdata.tmp', 'r') as f:
				content = f.read()
				size = len(content)
				start = 0
				while start < size:
					# Look for lines of text that begin with "temp_now: ' "
					start = content.find("temp_now: '",start)
					start = start if start != -1 else size
					# Once the line has been found, read the text until the '&'
					end = content.find("&",start)
					end = end if end != -1 else size
					# Set extracted_temp to the value of the text found starting at the 10th character
					extracted_temp = content[start + 10 : end]
					# Fall out of loop
					start = end + 1
					# Open tempfile.tmp
					tempfile = open('tempfile.tmp', 'w')
					# Write extracted_temp to tempfile.tmp
					print >> tempfile, extracted_temp
			# Close tempfile.tmp
			tempfile.close()

			# Extract raw temperature value
			raw_temp = open('tempfile.tmp', 'r').read()
	
			# Convert temperature value to an integer
			current_temp = int(float(raw_temp))
			
			# Handle temperature based on user preference (default is F)
			if (unit_pref == "C"):
				conversion = ((current_temp - 32) / 1.8)
				current_temp = int(float(conversion))
			display.disp.clear()
		else:
			weather_update_error = "true"

# Define draw unit function
def draw_unit():
	global unit_pref
	
	# Draw 'F' if user preference is Farenheit
	if (unit_pref == "F"):
        	display.writeDigitRaw(4,(1+32+16+64))
	
	# Draw 'C' if user preference is Celsius
	if (unit_pref == "C"):
        	display.writeDigitRaw(4,(1+32+16+8))

# Define display weather function
def displayweather():
	global current_temp

	# Handle single digit negative temperatures
	if ((current_temp < 0) and (current_temp >= -9)):
		neg_temp = abs(current_temp)
		# Draw negative symbol
		display.writeDigitRaw(0, 64)
		# Only digit of temperature
		display.writeDigit(1, int(neg_temp % 10))
		
	# Handle double digit negative temperatures
	if (current_temp <= -10):
		neg_temp = abs(current_temp)
		# Draw negative symbol
		display.writeDigitRaw(0, 64)
		# First digit of temperature
		display.writeDigit(1, int(neg_temp / 10))
		# Second digit of temperature
		display.writeDigit(3, neg_temp % 10)
			
	# Handle single digit positive temperatures
	if ((current_temp >= 0) and (current_temp < 10)):
		# Only digit of temperature (omitting zero)
		display.writeDigit(0, current_temp % 10)
			
	# Handle double digit positive temperatures
	if ((current_temp >= 10) and (current_temp < 100)):
		# First digit of temperature
		display.writeDigit(0, int(current_temp / 10))
		# Second digit of temperature
		display.writeDigit(1, current_temp % 10)
				
	# Handle triple digit positive temperatures
	if (current_temp >= 100):
		# First digit of temperature
		display.writeDigit(0, int(current_temp / 100))
		# Second digit of temperature
		display.writeDigit(1, current_temp % 10)
		# Third digit of temperature
		display.writeDigit(3, current_temp % 1)
		
	# Draw temperature unit
	draw_unit()
	
	# Cleanup Temp Files
	os.system("rm -r -f *.tmp")
	
# Define display time function
def displaytime():
	# Display current time
	# First digit of hour
	display.writeDigit(0, int(hour / 10))
	# Second digit of hour
	display.writeDigit(1, hour % 10)
	# First digit of minutes
	display.writeDigit(3, int(minute / 10))
	# Second digit of minutes
	display.writeDigit(4, minute % 10)
	# Toggle blinking colon
	display.writeDigitRaw(2,2)
	time.sleep(.75)
	display.writeDigitRaw(2,0)
	time.sleep(.75)
	

# Clear display and light all segments
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

display.setColon(True)
time.sleep(1)

foo = 0

# Start main loop
while(True):
	# If RPi is shutting down then run the "signal_handler" function
	signal.signal(signal.SIGTERM, signal_handler)
	# Check current time
	currenttime()
	
	# Set display brightness based on time of day
	if (auto_dimming == "enabled"):
		if (((minute == 0) and (second == 0)) or (foo == 0)):
			if ((hour >= 8) and (hour <= 15)):
				LEDBackpack().setBrightness(day_bright)
			else:
				LEDBackpack().setBrightness(night_bright)

	# If user preference is to show weather, then show temperature for 15 seconds at the beginning of each even minute
	if (show_weather == "yes"):
		if (second == 1) and ((minute % 10) == 0 or (minute % 10) == 2 or (minute % 10) == 4  or (minute % 10) == 6 or (minute % 10) == 8):
			weatherupdate()
			while(second <= 15) and (weather_update_error == "false"):
				displayweather()
				currenttime()
		# Show the current time
		else:
			displaytime()
	# If user preference is not to show weather then show current time
	else:
		displaytime()
	foo = 1
