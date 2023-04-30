#!/bin/bash

# Start the Python server
lxterminal -t "Python Server" -e "bash -c 'python3 script.py; $SHELL'"

# Wait for the server to start up
sleep 2

# Keep the script running to keep the terminal window open
while true; do
    sleep 1
done