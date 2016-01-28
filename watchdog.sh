#!/bin/bash

# Author: Sid Gadkari
# Last Revision: 12/21/2015 
# This script runs at boot and acts as a watchdog to start and restart any scripts that stop running for any reason.
# After updating this script, make it executable (chmod +x) and run at boot via /etc/rc.local.

# Main loop
while true
do
	# Check if the  processes are running. If it isn't then run the scripts.
	pgrep -f clock.py || python /usr/bin/rpi-clock/clock.py --silent &

	# Sleep for 120 sec. and then check process status again.
	sleep 60
done
