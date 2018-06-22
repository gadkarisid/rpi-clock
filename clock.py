# Copyright (c) 2015-2018 Sid Gadkari. All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Last Revision Date: 04/17/2018

#---------------------BEGIN USER PREFERENCES---------------------
# Define time format (12 or 24 hour)
hour_format = 12

# Define if you want to see weather information (yes/no)
show_weather = "yes"

# Define temperature unit (F or C)
unit_pref = "F"

# Define your Weather Underground API key
api_key = "ADD API KEY HERE"

# Define your US zip code
zipcode = "20001"

# Default display brightness (0 to 15)
default_brightness = 15

# Auto dimming based on time of day (enabled/disabled)
auto_dimming = "enabled"

# Display brightness during day (0 to 15)
day_bright = 15

# Display brightness during night (0 to 15)
night_bright = 7
#----------------------END USER PREFERENCES----------------------

#!/usr/bin/python

import time
import datetime
import signal
import sys
import json
import urllib2
from Adafruit_7Segment import *

# Initialize display
display = SevenSegment(address=0x70)
LEDBackpack().setBrightness(default_brightness)

# Change working directory
os.chdir('/usr/bin/rpi-clock')

# Set the hour offset based on user preference
hour_offset = 24 - hour_format

# Define display self-test function
def selftest():
	# Light all segments of the display to check for physical problems
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
	
# Define system signal handler function
def signal_handler(signal, frame):
	# If RPi is shutting down or rebooting clear the LED display
	display.disp.clear()
	sys.exit(0)

# Define current time function
def currenttime():
	global now
	global hour
	global minute
	global second
	global flag_getweather
	global flag_displayweather

	# Set flag default values
	flag_getweather = "false"
	flag_displayweather = "false"

	# Get current time
	now = datetime.datetime.now()
	hour = now.hour
	minute = now.minute
	second = now.second

	# If the current hour is greater than 12, reformat the hour to conform to the user preference setting
	if (hour > 12):
		hour = (now.hour - hour_offset)
	
	# Define condition to get current temperature
	if (second == 1) and (((minute % 10) == 3) or ((minute % 10) == 6)  or ((minute % 10) == 9)):
		flag_getweather = "true"

	# Deine condition to display the temperature 4 times a minute
	if ((second == 5) or (second == 20) or (second == 35) or (second == 50)):
		flag_displayweather = "true"

# Define weather update function
def weatherupdate():
	global current_temp
	global unit_pref
	global weather_update_error

	# Set weather_update_error to default value
	weather_update_error = "false"

	# Create URL for weather lookup
	url = "http://api.wunderground.com/api/" + api_key + "/conditions/q/" + zipcode + ".json"

	# Get weather conditions
	try:
		weatherdata = urllib2.urlopen(url)
		read_weather = weatherdata.read()
		parsed_weatherdata = json.loads(read_weather)
		# Parse current temperature in Fahrenheit
		if (unit_pref == "F"):
			parsed_temp = parsed_weatherdata['current_observation']['temp_f']
		# Parse current temperature in Celsius
		if (unit_pref == "C"):
			parsed_temp = parsed_weatherdata['current_observation']['temp_c']
		weatherdata.close()
		pass
	except:
		weather_update_error = "true"
		pass

	# Round Temperature to nearest integer
	current_temp = int(round(parsed_temp,0))

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

	# Clear the display
	display.disp.clear()

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
		display.writeDigit(1, current_temp % 1)
		# Third digit of temperature
		display.writeDigit(3, current_temp % 10)
		
	# Draw temperature unit
	draw_unit()
	
	# Show temperature for 5 seconds
	time.sleep(5)
	
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
	time.sleep(1)
	display.writeDigitRaw(2,0)
	time.sleep(1)

# Run display self-test when script starts before displaying time
selftest()

# Set flag when script is first run
foo = 0

# Start main loop
while(True):
	# Check current time
	currenttime()
	
	# If RPi is shutting down then run the "signal_handler" function and clear the LED display
	signal.signal(signal.SIGTERM, signal_handler)
		
	# First run behavior
	if (auto_dimming == "enabled"):
		if ((minute == 0) and (second <= 10)) or (foo == 0):
			if ((hour >= 7) and (hour <= 18)):
				LEDBackpack().setBrightness(day_bright)
			else:
				LEDBackpack().setBrightness(night_bright)
	if (foo == 0 and show_weather == "yes"):
		weatherupdate()
		foo = 1

	# Get updated weather info
	if ((show_weather == "yes") and (flag_getweather == "true")):
		try:
			weatherupdate()
			display.disp.clear()
			displayweather()
			pass
		except:
			displaytime()
			pass

	# Show current temperature
	if (show_weather == "yes" and flag_displayweather == "true" and weather_update_error == "false"):
		displayweather()

	# If user preference is not to show weather then show current time
	else:
		displaytime()
	
	# Flag to indicate that script has already been started to avoid resetting display brightness
	foo = 1

	# Check current time
	currenttime()
