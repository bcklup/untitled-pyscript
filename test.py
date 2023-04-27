import time
import os
import RPi.GPIO as GPIO

# Set up GPIO pins
stirrer_pins = [2, 3] # 2 pins

koh_pins = [4, 5, 6, 7] # 4 pins - stepper

heater_pin = 8 # on/off

solenoid_pins = [9, 10] # s

temp_pin = 11 # sensor

def main():
  while True:
    temp = GPIO.input(temp_pin)
    print("TEMP OUTPUT: \t", temp)
    time.sleep(2)

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