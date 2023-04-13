#!/bin/bash
# Wait for desktop environment to start
sleep 10

# Set terminal size
TERMINAL_WIDTH=120
TERMINAL_HEIGHT=34

# Launch terminal with Python script
x-terminal-emulator -e "bash -c 'cd ~/ && python script.py; exec bash'" --geometry=$TERMINAL_WIDTH"x"$TERMINAL_HEIGHT"+0+0 --fullscreen