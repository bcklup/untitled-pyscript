import RPi.GPIO as GPIO
import time
import os
import sys
# from threading import Event
# import socketio
# import eventlet
# from eventlet.green import threading

import datetime
import max6675
# from flask import Flask, send_from_directory
# from flask_cors import CORS

#-----------------------CONFIG VARIABLES---------------------
# Relay Pins
heater_pin = 11
stirrer_pin = 13
solenoid_pin = 15

# RBG Pins
red_pin = 29
green_pin = 31
blue_pin = 33

# Button Pins
button1_pin = 37
button2_pin = 32
abort_button = 36

# MAX6675 Temp sensor pins
temp_cs = 22
temp_sck = 18
temp_so = 16

# Condition Variables
HEAT_THRESHOLD_1 = 100
HEAT_THRESHOLD_2 = 70

# Timer Variables
LOOP_INTERVALS = 2
SOLENOID_TIMER = 1 # Interval between solenoid on->off
STAGE_1_TIMER = 30 # Run stirrer this long before turning on heating element
STAGE_1_RUNTIME = 60 # Runtime while 100deg
STAGE_1_PAUSE = 5 # Pause to cool down
STAGE_2_TIMER = 5 # isolated blend timer for stage 2

#------------------------END OF CONFIG VARIABLES--------------

# Init GPIO to BOARD mode
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


GPIO.setup(red_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(green_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(blue_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(heater_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(stirrer_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(solenoid_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(abort_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
max6675.set_pin(temp_cs, temp_sck, temp_so, 1)

# Create a socket.io server instance
# sio = socketio.Server(cors_allowed_origins='*')

# app = Flask(__name__)
# CORS(app)
# app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

lock = False
stage = 0
# should_abort = Event()
# tetemp_value = 34


def lightsOff():
  GPIO.output(red_pin,GPIO.HIGH)
  GPIO.output(green_pin,GPIO.HIGH)
  GPIO.output(blue_pin,GPIO.HIGH)

def redLight():
  GPIO.output(red_pin,GPIO.LOW)
  GPIO.output(green_pin,GPIO.HIGH)
  GPIO.output(blue_pin,GPIO.HIGH)

def greenLight():
  GPIO.output(red_pin,GPIO.HIGH)
  GPIO.output(green_pin,GPIO.LOW)
  GPIO.output(blue_pin,GPIO.HIGH)

def blueLight():
  GPIO.setmode(GPIO.BOARD)
  GPIO.output(red_pin,GPIO.HIGH)
  GPIO.output(green_pin,GPIO.HIGH)
  GPIO.output(blue_pin,GPIO.LOW)

def log(text):
  print(text)
  # try:
  #   sio.start_background_task(sio.emit('log', '[{0}]{1}'.format(datetime.datetime.now().strftime("%H:%M:%S %p"), text)))
  # except:
  #     print('{1}'.format(text))

# Define event handlers for socket.io events
# @sio.on('connect')
# def connect(sid, environ):
#   global lock
#   GPIO.setmode(GPIO.BOARD)
#   blueLight()
#   log('[SERV] Connected: ${0}'.format(sid))
#   if not lock:
#     lock = True

#     def temperature_update():
#       log('[BG] Background Task \'temperature_update\' Started.')
#       while True:
#         global temp_value
#         new_temp_value = max6675.read_temp(temp_cs)

#         if new_temp_value < 500 and new_temp_value > 10:
#           temp_value = new_temp_value

#         # Emit the temperature value to the connected client
#         sio.start_background_task(sio.emit('temp', temp_value))

#         max6675.time.sleep(2)

#     sio.start_background_task(temperature_update)
#     # eventlet.spawn(temperature_update)

#     log('[OP] System is ready. Start Stage 1 or 2?')
#     lock = False
#     sio.start_background_task(sio.emit('ready'))
#   else:
#       log('[ERR] Another operation is in progress.')


# @sio.on('disconnect')
# def disconnect(sid):
#   print('[SERV] Disconnected:', sid)
#   #GPIO.cleanup()

# @sio.on('abort')
def abort():
  global stage
  log('[OP] Aborting system and restart')
  redLight()
  # global should_abort
  # should_abort.set()
  lock = False
  GPIO.cleanup()
  time.sleep(2)
  stage = 0
  os.execl(sys.executable, sys.executable, *sys.argv)
  # should_abort.clear()
  # blueLight()
  # restart()

def restart():
  global lock
  if not lock:
    blueLight()
    log('---------------------------------------')
    log('[OP] Restarting...')
    log('---------------------------------------')

    GPIO.output(heater_pin, GPIO.HIGH)
    GPIO.output(stirrer_pin, GPIO.HIGH)
    GPIO.output(solenoid_pin, GPIO.HIGH)
    
    lock = False
    # sio.emit('restart')
  else:
    log('[ERR] Another operation is in progress.')


# @sio.on('stage1_trigger')
def stage1_trigger():
  global lock
  global stage
  if not lock:
    stage = 1
    # global should_abort
    lock = True
    greenLight()
    # sio.start_background_task(sio.emit('stage1_start'))
    log('---------------------------------------')
    log('[STAGE 1 Stage 1 Starting...')
    log('[GPIO] Stirrer ON for {0} seconds...'.format(STAGE_1_TIMER))
    GPIO.output(stirrer_pin, GPIO.LOW)

    # should_abort.wait(STAGE_1_TIMER)
    time.sleep(STAGE_1_TIMER)

    log('[GPIO] Heater ON')
    GPIO.output(heater_pin, GPIO.LOW)

    log('[STAGE 1] Waiting for temperature to reach Stage 1 threshold ({0}deg Celcius)'.format(HEAT_THRESHOLD_1))
    # Monitor temperature
    while True:
      temp_value = max6675.read_temp(temp_cs)
      print('[TEMP] {0}deg celcius'.format(temp_value))
      # sio.start_background_task(sio.emit('temp', temp_value))
      if temp_value >= HEAT_THRESHOLD_1:
          log("[STAGE 1] Temperature reached Stage 1 threshold.")
          log("[STAGE 1] Continuing for another {0} seconds...".format(STAGE_1_RUNTIME))
          time.sleep(STAGE_1_RUNTIME) # wait for 1 minute
          break
      else:
          # max6675.time.sleep(LOOP_INTERVALS)
          time.sleep(LOOP_INTERVALS)

    log('[STAGE 1] Heating and blending complete.')
  
    log('[GPIO] Stirrer OFF')
    GPIO.output(stirrer_pin, GPIO.HIGH)
    log('[GPIO] Heater OFF')
    GPIO.output(heater_pin, GPIO.HIGH)

    log('[STAGE 1] Cooling down...')
    time.sleep(STAGE_1_PAUSE)

    blueLight()
    lock = False
    # sio.start_background_task(sio.emit('ready'))
  else:
    log('[ERR] Another operation is in progress.')

# @sio.on('stage1_response_cooling')
# def stage1_response_cooling(sid, answer):
#   global lock
#   if not lock:
#     lock = True
#     if answer is True:
#       sio.start_background_task(sio.emit('stage1_start'))
#       log('[STAGE 1] Cooling down...')
#       should_abort.wait(STAGE_1_PAUSE)

#       log('[PROMPT] Continue? (Has it cooled sufficiently?)')
#       lock = False
#       sio.emit('stage1_prompt_cooling')
#     else:
#       log('[STAGE 1] Stage 1 Completed. Proceed to Stage 2?')
#       lock = False
#       sio.emit('stage2_prompt_trigger')

#   else:
#     log('[ERR] Another operation is in progress.')
       
# @sio.on('stage2_trigger')
def stage2_trigger():
  global lock
  global stage
  if not lock:
    stage = 2
    lock = True
    greenLight()
    # sio.start_background_task(sio.emit('stage2_start'))
    log('---------------------------------------')
    log('[STAGE 2] Stage 2 Starting...')

    log('[GPIO] Solenoid open for {0} seconds.'.format(SOLENOID_TIMER))
    GPIO.output(solenoid_pin, GPIO.LOW)
    time.sleep(SOLENOID_TIMER)
    GPIO.output(solenoid_pin, GPIO.HIGH)

    log('[GPIO] Stirrer ON for {0} seconds...'.format(STAGE_2_TIMER))
    GPIO.output(stirrer_pin, GPIO.LOW)

    log('[GPIO] Heater ON')
    GPIO.output(heater_pin, GPIO.LOW)

    log('[STAGE 2] Waiting for temperature to reach Stage 2 threshold ({0}deg Celcius)'.format(HEAT_THRESHOLD_2))

    while True:
      temp_value = max6675.read_temp(temp_cs)
      print('[TEMP] {0}deg celcius'.format(temp_value))
      # sio.start_background_task(sio.emit('temp', temp_value))

      if temp_value >= HEAT_THRESHOLD_2:
        log("[STAGE 2] Temperature reached Stage 2 threshold.")
        break
      else:
        time.sleep(LOOP_INTERVALS)

    GPIO.output(heater_pin, GPIO.HIGH)
    log('[GPIO] Heater OFF')
    GPIO.output(stirrer_pin, GPIO.HIGH)
    log('[GPIO] Stirrer OFF')

    log('[STAGE 2] Process complete. Cleaning up and restarting...')
    time.sleep(2)
    blueLight()
    lock = False
    restart()

  else:
    log('[ERR] Another operation is in progress.')

def btn1_event():
  stage1_trigger()

def btn2_event():
  global lock
  global stage
  print(f'[DEBUG] Lock is {0}, Stage: {1}'.format(lock, stage))
  if lock is True: return

  if stage == 0:
    stage1_trigger()
  if stage == 1:
    stage2_trigger()
  if stage == 2:
    abort()

def abort_btn_event():
  abort('')

# GPIO.add_event_detect(button1_pin, GPIO.FALLING, callback=btn1_event, bouncetime=300)
# GPIO.add_event_detect(button2_pin, GPIO.FALLING, callback=btn2_event, bouncetime=300)
# GPIO.add_event_detect(abort_button, GPIO.RISING, callback=abort_btn_event, bouncetime=300)

blueLight()

# # Serve the built React app files
# @app.route('/')
# def serve_client():
#   return send_from_directory('client/build', 'index.html')

# @app.route('/favicon.ico')
# def serve_icon():
#   return send_from_directory('client/build', 'favicon.ico')

# @app.route('/static/<path:path>')
# def serve_static(path):
#   return send_from_directory('client/build/static', path)

# @app.route('/static/js/<path:path>')
# def serve_js(path):
#   return send_from_directory('client/build/static/js', path)

# @app.route('/static/css/<path:path>')
# def serve_css(path):
#   return send_from_directory('client/build/static/css', path)


# Start the server
# if __name__ == '__main__':
    # eventlet.spawn(temperature_update)
    # wsgi_server_greenlet = eventlet.spawn(temperature_update)

    # eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

# while True: pass
while True:
  # btn1 = GPIO.input(button1_pin)
  btn2 = GPIO.input(button2_pin)
  # print(btn2)
  # btn3 = GPIO.input(abort_button)
  # print(btn1, btn2, btn3)
  # if btn3 is True:
  #   abort_btn_event()
  # elif btn1 is True:
  #   btn1_event()
  if btn2 == 1:
    btn2_event()


GPIO.cleanup()