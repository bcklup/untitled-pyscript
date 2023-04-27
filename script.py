import time
import os
# import RPi.GPIO as GPIO

# Set up GPIO pins
stirrer_pins = [2, 3] # 2 pins

koh_pins = [4, 5, 6, 7] # 4 pins - stepper

heater_pin = 8 # on/off

solenoid_pins = [9, 10] # s

temp_pin = 11 # sensor

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(shredder_pin, GPIO.OUT)
# GPIO.setup(stepper_pin, GPIO.OUT)
# GPIO.setup(stirrer_pin, GPIO.OUT)
# GPIO.setup(heater_pin, GPIO.OUT)
# GPIO.setup(urea_pin, GPIO.OUT)
# GPIO.setup(citric_pin, GPIO.OUT)
# GPIO.setup(temp_pin, GPIO.IN)

# Define threshold temperatures
HEAT_THRESHOLD_1 = 100
HEAT_THRESHOLD_2 = 70

LOOP_INTERVALS = 1

# Define stage timers
STAGE_1_TIMER = 6 # Run while heater, stirrer, etc. are on and sensor is at 100+C
STAGE_1_PAUSE = 5

# Define motor and output control functions

def koh(toggle):
    # if (toggle): GPIO.output(stepper_pin, GPIO.HIGH)
    # else: GPIO.output(stepper_pin, GPIO.LOW)

    print("[GPIO] Stepper Motor\t\t-\t", '[ON]' if toggle else '[OFF]')


def stirrer(toggle):
    # if (toggle): GPIO.output(stirrer_pin, GPIO.HIGH)
    # else: GPIO.output(stirrer_pin, GPIO.LOW)

    print("[GPIO] Stirrer DC Motor\t\t-\t", '[ON]' if toggle else '[OFF]')


def heater(toggle):
    # if (toggle): GPIO.output(heater_pin, GPIO.HIGH)
    # else: GPIO.output(heater_pin, GPIO.LOW)

    print("[GPIO] Heating Element\t\t-\t", '[ON]' if toggle else '[OFF]')

def solenoid(toggle):
    # if (toggle): GPIO.output(urea_pin, GPIO.HIGH)
    # else: GPIO.output(urea_pin, GPIO.LOW)

    print("[GPIO] Solenoid for Citric + Urea Acid\t\t-\t", '[ON]' if toggle else '[OFF]')

def parseTemp(sensor_val):
    parsedSensorVal = sensor_val
    #Parsing proper
    return parsedSensorVal

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Define stage 1 method
def stage_1():
    clearScreen()
    print ("\nStage 1")
    print("-----------------------------------------------------------------\n")
    # Turn on motors and outputs
    koh(True)
    stirrer(True)
    heater(True)

    # time.sleep(2)


    # Monitor temperature
    while True:
        # temp = GPIO.input(temp_pin)
        rawTemp = 110
        temp = parseTemp(rawTemp)
        clearScreen()
        print ("\nStage 1")
        print("-----------------------------------------------------------------\n")
        print("[GPIO] Temperature Sensor\t-\t[", temp, "deg C]")
        if temp >= HEAT_THRESHOLD_1:
            clearScreen()
            print ("\nStage 1")
            print("-----------------------------------------------------------------\n")
            print("\nTemperature reached Stage 1 Threshold (", HEAT_THRESHOLD_1, "deg C )\n")
            print("\nHeat-up Timer\t\t-\t",STAGE_1_TIMER,"ms...")
            time.sleep(STAGE_1_TIMER) # wait for 1 minute
            break
        else: time.sleep(LOOP_INTERVALS)

    print("\nHeat-up Lapsed...\nStopping motors and heating elements...\nCooling down...\n")

    # Turn off motors and outputs
    koh(False)
    stirrer(False)
    heater(False)

    # 5s wait
    # Check if cooled down
    while True:
        time.sleep(STAGE_1_PAUSE);
        if input("\nEnter A to Continue (cooled sufficiently?). Enter B to wait again: ") == 'A':
            break

    # Prompt to continue or reset
    clearScreen()
    print ("\nStage 1")
    print("-----------------------------------------------------------------\n")
    if input("Stage 1 Completed.\nProceed to Stage 2? [A] - Yes, [B] - No: ") == 'A':
        stage_2()
    else:
        main_loop()

# Define stage 2 method
def stage_2():
    clearScreen()
    print ("\nStage 2")
    print("-----------------------------------------------------------------\n")

    # Turn on outputs
    stirrer(True)
    heater(True)
    solenoid(True)

    # time.sleep(2)

    # Monitor temperature
    while True:
        # temp = parseTemp(GPIO.input(temp_pin))
        rawTemp = 80
        temp = parseTemp(rawTemp)
        clearScreen()
        print ("\nStage 2")
        print("-----------------------------------------------------------------\n")
        print("[GPIO] Temperature Sensor\t-\t[", temp, "deg C]")
        if temp >= HEAT_THRESHOLD_2:
            clearScreen()
            print ("\nStage 2")
            print("-----------------------------------------------------------------\n")
            print("\nTemperature reached Stage 2 Threshold (", HEAT_THRESHOLD_2, "deg C )\n")
            reset_all()

            print("\nProcess complete.\nReturning to main menu...")
            time.sleep(2)
            main_loop()
        # elif input("\nEnter B to stop: ") == 'B':
        #     reset_all()
        #     return
        else: time.sleep(LOOP_INTERVALS)


# Define reset function
def reset_all():
    koh(False)
    stirrer(False)
    heater(False)
    solenoid(False)

# Define main loop method
def main_loop():
    while True:
        clearScreen()
        print("-----------------------------------------------------------------")
        print ("\t\t\tMain Program Loop")
        print("-----------------------------------------------------------------\n")
        print("\nNOTE: You can close the program anytime with Ctrl+X.\nMotors and Sensors may not close properly.\n")
        choice = input("\nPress A to start. B to quit: ")
        if choice.upper() == "B":
            # GPIO.cleanup()
            quit()
        elif choice.upper() == "A":
            stage_1()

if __name__ == "__main__":
    main_loop()