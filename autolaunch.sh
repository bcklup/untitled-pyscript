#!/bin/bash

# Start the Python server
lxterminal -t "Python Server" -e "bash -c 'python3 ~/untitled-pyscript/script.py; $SHELL'"
lxterminal -t "Web Server" -e "bash -c 'serve ~/untitled-pyscript/client/build; $SHELL'"

# Wait for the server to start up
sleep 2

# Open the Raspberry Pi OS default browser to localhost:5000
xdg-open "http://localhost:3000"

# Keep the script running to keep the terminal window open
while true; do
    sleep 1
done