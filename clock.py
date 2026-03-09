#!/usr/bin/env python3

# Copyright (c) 2015-2026 Sid Gadkari. All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Last Revision Date: 2026-03-09

#---------------------BEGIN USER PREFERENCES-------------
# Define time format (12 or 24 hour)
hour_format = 24

# Define if you want to see weather information (yes/no)
show_weather = "yes"

# Define temperature unit (F or C)
unit_pref = "F"

# Define your Open Weather Map API key
api_key = "ADD API KEY"

# Define your zip code
zip_code = "ADD ZIP CODE"

# Default display brightness (0.0 to 1.0)
default_brightness = 1.0

# Auto dimming based on time of day (enabled/disabled)
auto_dimming = "enabled"

# Display brightness during day (0.0 to 1.0)
day_bright = 0.5

# Display brightness during night (0.0 to 1.0)
night_bright = 0.2

# Maximum number of boot network wait attempts (5 second sleep between each)
network_wait_attempts = 12

# Number of consecutive weather fetch failures before suppressing display
# This prevents a single transient failure from permanently latching the error flag
weather_error_threshold = 3

#----------------------END USER PREFERENCES--------------

import os
import time
import datetime
import signal
import sys
import json
import socket
import urllib.request
import urllib.error
from board import SCL, SDA
import busio
from adafruit_ht16k33.segments import Seg7x4

# Initialize I2C bus
i2c = busio.I2C(SCL, SDA)

# Initialize display
display = Seg7x4(i2c, address=0x70)
display.brightness = default_brightness

# Change working directory
os.chdir('/usr/bin/rpi-clock')

# Set the hour offset based on user preference
hour_offset = 24 - hour_format

# Track consecutive weather fetch failures instead of a simple boolean latch
weather_error_count = 0

# Set the hour offset based on user preference
hour_offset = 24 - hour_format

# Define display self-test function
def selftest():
    """Light all segments of the display to check for physical problems"""
    for position in [0, 1, 2, 3]:
        display.set_digit_raw(position, 0b00000001)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b00000011)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b00000111)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b00001111)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b00011111)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b00111111)
        time.sleep(0.12)
        display.set_digit_raw(position, 0b01111111)
        time.sleep(0.12)

    display.colon = True
    time.sleep(1)

# Define system signal handler function
def signal_handler(sig, frame):
    """If RPi is shutting down or rebooting clear the LED display"""
    display.fill(0)
    sys.exit(0)

# Define network readiness check
def wait_for_network():
    """
    Block until DNS resolution succeeds or we exhaust attempts.
    Prevents the boot race condition where systemd-resolved isn't
    fully up before the script's first weather fetch.
    """
    for attempt in range(1, network_wait_attempts + 1):
        try:
            socket.getaddrinfo("api.openweathermap.org", 443)
            print(f"Network ready after {attempt} attempt(s).")
            return True
        except socket.gaierror:
            print(f"Network not ready, attempt {attempt}/{network_wait_attempts}. Waiting 5s...")
            time.sleep(5)
    print("Network did not become ready in time. Weather disabled until next successful fetch.")
    return False

# Define current time function
def currenttime():
    """Get current time and set flags for weather updates"""
    global now
    global hour
    global minute
    global second
    global flag_getweather
    global flag_displayweather

    # Set flag default values
    flag_getweather = False
    flag_displayweather = False

    # Get current time
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    # If the current hour is greater than 12, reformat the hour to conform to the user preference setting
    if hour > 12:
        hour = now.hour - hour_offset

    # Define condition to get current temperature
    if (second <= 4) and ((minute % 10) in [3, 6, 9]):
        flag_getweather = True

    # Define condition to display the temperature 4 times a minute
    if second in [5, 20, 35, 50]:
        flag_displayweather = True

# Define weather update function
def weatherupdate():
    """Fetch current temperature from OpenWeatherMap API"""
    global current_temp
    global weather_error_count

    # Define unit preference
    if unit_pref == "F":
        unit_name = "imperial"
    elif unit_pref == "C":
        unit_name = "metric"
    else:
        unit_name = "imperial"

    # Create URL for weather lookup
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code}&units={unit_name}&appid={api_key}"

    # Get weather conditions
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            read_weather = response.read()
            parsed_weatherdata = json.loads(read_weather)

        parsed_temp = parsed_weatherdata['main']['temp']

        # Round temperature to nearest integer
        current_temp = int(round(parsed_temp, 0))

        # Successful fetch — reset error counter so display recovers automatically
        weather_error_count = 0
        print(f"Weather updated: {current_temp}{unit_pref}")

    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as e:
        weather_error_count += 1
        print(f"Weather update error ({weather_error_count}/{weather_error_threshold}): {e}")

# Define helper to check if weather display should be suppressed
def weather_ok():
    """Returns True if weather data is usable (error count below threshold)"""
    return weather_error_count < weather_error_threshold

# Define draw unit function
def draw_unit():
    """Draw temperature unit (F or C) on the display"""
    if unit_pref == "F":
        display.set_digit_raw(3, 0b01110001)
    elif unit_pref == "C":
        display.set_digit_raw(3, 0b00111001)

# Define display weather function
def displayweather():
    """Display current temperature on the LED display"""
    global current_temp

    # Clear the display
    display.fill(0)

    try:
        # Handle single digit negative temperatures
        if -9 <= current_temp < 0:
            neg_temp = abs(current_temp)
            display.set_digit_raw(0, 0b01000000)
            display[1] = str(neg_temp % 10)

        # Handle double digit negative temperatures
        elif current_temp <= -10:
            neg_temp = abs(current_temp)
            display.set_digit_raw(0, 0b01000000)
            display[1] = str(neg_temp // 10)
            display[3] = str(neg_temp % 10)

        # Handle single digit positive temperatures
        elif 0 <= current_temp < 10:
            display[0] = str(current_temp % 10)

        # Handle double digit positive temperatures
        elif 10 <= current_temp < 100:
            display[0] = str(current_temp // 10)
            display[1] = str(current_temp % 10)

        # Handle triple digit positive temperatures
        elif current_temp >= 100:
            display[0] = str(current_temp // 100)
            display[1] = str((current_temp % 100) // 10)
            display[3] = str(current_temp % 10)

        # Draw temperature unit
        draw_unit()

        # Show temperature for 5 seconds
        time.sleep(5)

    except Exception as e:
        print(f"Display weather error: {e}")
        return

# Define display time function
def displaytime():
    """Display current time on the LED display"""
    display[0] = str(hour // 10)
    display[1] = str(hour % 10)
    display[2] = str(minute // 10)
    display[3] = str(minute % 10)

    display.colon = True
    time.sleep(1)
    display.colon = False
    time.sleep(1)

# Main execution
if __name__ == "__main__":
    # Run display self-test
    selftest()

    # Set flag when script is first run
    first_run = True

    # Register signal handler for clean shutdown
    signal.signal(signal.SIGTERM, signal_handler)

    # Wait for network before attempting first weather fetch
    # This resolves the boot race condition with systemd-resolved
    if show_weather == "yes":
        wait_for_network()

    # Start main loop
    try:
        while True:
            # Check current time
            currenttime()

            # Auto dimming logic
            if auto_dimming == "enabled":
                if (minute == 0 and second <= 10) or first_run:
                    if 7 <= hour <= 18:
                        display.brightness = day_bright
                    else:
                        display.brightness = night_bright

            # First run weather update
            if first_run and show_weather == "yes":
                weatherupdate()
                first_run = False

            # Get updated weather info
            if show_weather == "yes" and flag_getweather and weather_ok():
                weatherupdate()
                display.fill(0)
                displayweather()
            else:
                displaytime()

            # Show current temperature periodically
            if show_weather == "yes" and flag_displayweather and weather_ok():
                displayweather()
            else:
                displaytime()

            # Check current time again at end of loop
            currenttime()

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        display.fill(0)
        sys.exit(0)