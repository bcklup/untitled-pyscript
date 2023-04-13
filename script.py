import time
# import RPi.GPIO as GPIO

# Set up GPIO pins
shredder_pin = 2
stepper_pin = 3
stirrer_pin = 4
heater_pin = 5
urea_pin = 6
citric_pin = 7
temp_pin = 8

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

# Define stage timers
STAGE_1_TIMER = 60 # Run while heater, stirrer, etc. are on and sensor is at 100+C
STAGE_1_PAUSE = 5

# Define motor and output control functions
def shredder(toggle):
    # if (toggle): GPIO.output(shredder_pin, GPIO.HIGH)
    # else: GPIO.output(shredder_pin, GPIO.LOW)

    print("Shredder ", 'on' if toggle else 'off')

def stepper(toggle):
    # if (toggle): GPIO.output(stepper_pin, GPIO.HIGH)
    # else: GPIO.output(stepper_pin, GPIO.LOW)

    print("Stepper ", 'on' if toggle else 'off')


def stirrer(toggle):
    # if (toggle): GPIO.output(stirrer_pin, GPIO.HIGH)
    # else: GPIO.output(stirrer_pin, GPIO.LOW)

    print("Stirrer ", 'on' if toggle else 'off')

def heater(toggle):
    # if (toggle): GPIO.output(heater_pin, GPIO.HIGH)
    # else: GPIO.output(heater_pin, GPIO.LOW)

    print("Heater ", 'on' if toggle else 'off')

def urea(toggle):
    # if (toggle): GPIO.output(urea_pin, GPIO.HIGH)
    # else: GPIO.output(urea_pin, GPIO.LOW)

    print("Urea Solenoid ", 'on' if toggle else 'off')

def citric(toggle):
    # if (toggle): GPIO.output(citric_pin, GPIO.HIGH)
    # else: GPIO.output(citric_pin, GPIO.LOW)

    print("Citric Solenoid ", 'on' if toggle else 'off')

# Define stage 1 method
def stage_1():
    # Turn on motors and outputs
    shredder(True)
    stepper(True)
    stirrer(True)
    heater(True)

    # Monitor temperature
    while True:
        # temp = GPIO.input(temp_pin)
        temp = 60
        print("Current temp:", temp)
        if temp >= HEAT_THRESHOLD_1:
            print("Temperature reached threshold 1")
            time.sleep(STAGE_1_TIMER) # wait for 1 minute


            break
        elif input("Enter X to stop: ") == 'X':
            reset_all()
            return

    print("1 minute lapsed")

    # Turn off motors and outputs
    shredder(False)
    stepper(False)
    stirrer(False)
    heater(False)

    # 5s wait
    # Check if cooled down
    while True:
        time.sleep(STAGE_1_PAUSE);
        if input("Press Y to Continue: ") == 'Y':
            break

    # Prompt to continue or reset
    if input("Continue? (Y/N): ") == 'Y':
        stage_2()
    else:
        main_loop()

# Define stage 2 method
def stage_2():
    # Turn on outputs
    stirrer(True)
    heater(True)
    urea(True)
    citric(True)

    # Monitor temperature
    while True:
        # temp = GPIO.input(temp_pin)
        temp = 90
        print("Current temp:", temp)
        if temp >= HEAT_THRESHOLD_2:
            print("Temperature reached threshold 2")
            reset_all()
            print("Process complete.")
            main_loop()
        elif input("Enter X to stop: ") == 'X':
            reset_all()
            return

# Define reset function
def reset_all():
    shredder(False)
    stepper(False)
    stirrer(False)
    heater(False)
    urea(False)
    citric(False)

# Define main loop method
def main_loop():
    while True:
        choice = input("Press S to start or Q to quit: ")
        if choice.upper() == "Q":
            # GPIO.cleanup()
            break;
        elif choice.upper() == "S":
            stage_1()

if __name__ == "__main__":
    main_loop()