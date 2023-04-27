import time
import os
import RPi.GPIO as GPIO

import max6675

cs = 22
sck = 18
so = 16

max6675.set_pin(cs, sck, so, 1)

def main():
  while True:
    a = max6675.read_temp(cs)

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