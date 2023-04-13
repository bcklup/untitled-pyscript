import time
import RPi.GPIO as GPIO

# GPIO pin numbers for sensors and outputs
TEMP_SENSOR_PIN = 18
SHREDDER_PIN = 23
STEPPER_PIN = 24
STIRRER_PIN = 25
HEATER_PIN = 8
UREA_PIN = 7
CITRIC_PIN = 12

# Threshold temperatures for stage 1 and stage 2
HEAT_THRESHOLD_1 = 50
HEAT_THRESHOLD_2 = 80

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHREDDER_PIN, GPIO.OUT)
GPIO.setup(STEPPER_PIN, GPIO.OUT)
GPIO.setup(STIRRER_PIN, GPIO.OUT)
GPIO.setup(HEATER_PIN, GPIO.OUT)
GPIO.setup(UREA_PIN, GPIO.OUT)
GPIO.setup(CITRIC_PIN, GPIO.OUT)
GPIO.setup(TEMP_SENSOR_PIN, GPIO.IN)

def main_loop():
    while True:
        choice = input("Press S to start or Q to quit: ")
        if choice.upper() == "Q":
            GPIO.cleanup()
            break
        elif choice.upper() == "S":
            stage_1()

def stage_1():
    print("Starting stage 1...")
    GPIO.output(SHREDDER_PIN, GPIO.HIGH)
    GPIO.output(STEPPER_PIN, GPIO.HIGH)
    GPIO.output(STIRRER_PIN, GPIO.HIGH)
    GPIO.output(HEATER_PIN, GPIO.HIGH)
    while True:
        if GPIO.input(TEMP_SENSOR_PIN) > HEAT_THRESHOLD_1:
            print("Temperature threshold reached, starting timer...")
            time.sleep(60)
            break
    GPIO.output(SHREDDER_PIN, GPIO.LOW)
    GPIO.output(STEPPER_PIN, GPIO.LOW)
    GPIO.output(STIRRER_PIN, GPIO.LOW)
    GPIO.output(HEATER_PIN, GPIO.LOW)
    choice = input("Continue to stage 2? Y/N: ")
    if choice.upper() == "Y":
        stage_2()

def stage_2():
    print("Starting stage 2...")
    GPIO.output(STIRRER_PIN, GPIO.HIGH)
    GPIO.output(HEATER_PIN, GPIO.HIGH)
    GPIO.output(UREA_PIN, GPIO.HIGH)
    GPIO.output(CITRIC_PIN, GPIO.HIGH)
    while True:
        if GPIO.input(TEMP_SENSOR_PIN) > HEAT_THRESHOLD_2:
            print("Temperature threshold reached, finishing...")
            GPIO.output(STIRRER_PIN, GPIO.LOW)
            GPIO.output(HEATER_PIN, GPIO.LOW)
            GPIO.output(UREA_PIN, GPIO.LOW)
            GPIO.output(CITRIC_PIN, GPIO.LOW)
            break
    main_loop()

if __name__ == "__main__":
    main_loop()