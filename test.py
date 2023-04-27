import time
import os
from machine import Pin
from max6675 import MAX6675

import max6675

cs = 22
sck = 18
so = 16

soPIN = Pin(cs, Pin.IN)
sckPIN = Pin(sck, Pin.OUT)
csPIN = Pin(cs, Pin.OUT)

max = MAX6675(sckPIN, csPIN , soPIN)

def main():
  while True:
    a = max.read()

    # print temperature
    print("TEMP OUTPUT: \t", a)

    # when there are some errors with sensor, it return "-" sign and CS pin number
    # in this case it returns "-22" 
    
    max6675.time.sleep(2)

def main_loop():
    while True:
        print("-----------------------------------------------------------------")
        print ("\t\t\tMain Program Loop")
        print("-----------------------------------------------------------------\n")
        choice = input("\nPress A to start. B to quit: ")
        if choice.upper() == "B":
            # GPIO.cleanup()
            quit()
        elif choice.upper() == "A":
            main()

if __name__ == "__main__":
    main_loop()