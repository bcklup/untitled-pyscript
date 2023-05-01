import RPi.GPIO as GPIO
import time
import socketio
import eventlet
from eventlet.green import threading

import datetime
import max6675
from flask import Flask, send_from_directory
# from flask_cors import CORS

#-----------------------CONFIG VARIABLES---------------------
# Relay Pins
heater_pin = 11
stirrer_pin = 13
solenoid_pin = 15

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
STAGE_1_TIMER = 6 # Run while heater, stirrer, etc. are on and sensor is at 100+C
STAGE_1_PAUSE = 5

#------------------------END OF CONFIG VARIABLES--------------

# Init GPIO to BOARD mode
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


# Create a socket.io server instance
sio = socketio.Server(cors_allowed_origins='*')

app = Flask(__name__)
# CORS(app)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

lock = False
temp_value = 34

def log(text):
  print(text)
  try:
    sio.start_background_task(sio.emit('log', '[{0}]{1}'.format(datetime.datetime.now().strftime("%H:%M:%S %p"), text)))
  except:
      print('{1}'.format(text))

# Define event handlers for socket.io events
@sio.on('connect')
def connect(sid, environ):
  global lock
  log('[SERV] Connected: ${0}'.format(sid))
  if not lock:
    lock = True
    log('[GPIO] GPIO Setting up...')

    try:
      GPIO.setup(heater_pin, GPIO.OUT, initial=GPIO.HIGH)
      GPIO.setup(stirrer_pin, GPIO.OUT, initial=GPIO.HIGH)
      GPIO.setup(solenoid_pin, GPIO.OUT, initial=GPIO.HIGH)

      # max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
      max6675.set_pin(temp_cs, temp_sck, temp_so, 1)

      log('[GPIO] GPIO Set up SUCCESS.')
    except:
      log('[GPIO][ERR] GPIO Set up FAILED. Please check all GPIO connections')

    # sio.start_background_task(temperature_update)
    # eventlet.spawn(temperature_update)

    log('[OP] System is ready. Start Stage 1?')
    lock = False
    sio.start_background_task(sio.emit('ready'))
  else:
      log('[ERR] Another operation is in progress.')

def temperature_update():
  log('[BG] Background Task \'temperature_update\' Started.')
  while True:
      global temp_value
      temp_value = max6675.read_temp(temp_cs)

      # Emit the temperature value to the connected client
      sio.emit('temp', temp_value)

      max6675.time.sleep(2)
      time.sleep(2)

@sio.on('disconnect')
def disconnect(sid):
  print('[SERV] Disconnected:', sid)
  GPIO.cleanup()

@sio.on('abort')
def abort(data):
  log('[OP] Aborting system.. GPIO cleanup and restart')
  time.sleep(1)
  lock = False
  restart()

def restart():
  global lock
  if not lock:
    lock = True
    log('---------------------------------------')
    log('[OP] Restarting...')
    log('---------------------------------------')

    GPIO.output(heater_pin, GPIO.HIGH)
    GPIO.output(stirrer_pin, GPIO.HIGH)
    GPIO.output(solenoid_pin, GPIO.HIGH)
    
    lock = False
    sio.emit('restart')
  else:
    log('[ERR] Another operation is in progress.')


@sio.on('stage1_trigger')
def stage1_trigger(sid):
  global lock
  if not lock:
    lock = True
    sio.start_background_task(sio.emit('stage1_start'))
    log('---------------------------------------')
    log('[STAGE 1 Stage 1 Starting...')
    log('[GPIO] Stirrer ON')
    GPIO.output(stirrer_pin, GPIO.LOW)
    log('[GPIO] Heater ON')
    GPIO.output(heater_pin, GPIO.LOW)

    log('[STAGE 1] Waiting for temperature to reach Stage 1 threshold ({0}deg Celcius)'.format(HEAT_THRESHOLD_1))
    # Monitor temperature
    while True:
      global temp_value
      temp_value = max6675.read_temp(temp_cs)
      sio.start_background_task(sio.emit('temp', temp_value))
      if temp_value >= HEAT_THRESHOLD_1:
          log("[STAGE 1] Temperature reached Stage 1 threshold.")
          log("[STAGE 1] Continuing for another {0} seconds...".format(STAGE_1_TIMER))
          time.sleep(STAGE_1_TIMER) # wait for 1 minute
          break
      else:
          max6675.time.sleep(LOOP_INTERVALS)

    log('[STAGE 1] Heating and blending complete.')
  
    log('[GPIO] Stirrer OFF')
    GPIO.output(stirrer_pin, GPIO.HIGH)
    log('[GPIO] Heater OFF')
    GPIO.output(heater_pin, GPIO.HIGH)

    log('[STAGE 1] Cooling down...')
    time.sleep(STAGE_1_PAUSE)
    log('[PROMPT] Continue? (Has it cooled sufficiently?)')
    lock = False
    sio.emit('stage1_prompt_cooling')

  else:
    log('[ERR] Another operation is in progress.')

@sio.on('stage1_response_cooling')
def stage1_response_cooling(sid, answer):
  global lock
  if not lock:
    lock = True
    if answer is True:
      sio.start_background_task(sio.emit('stage1_start'))
      log('[STAGE 1] Cooling down...')
      time.sleep(STAGE_1_PAUSE)

      log('[PROMPT] Continue? (Has it cooled sufficiently?)')
      lock = False
      sio.emit('stage1_prompt_cooling')
    else:
      log('[STAGE 1] Stage 1 Completed. Proceed to Stage 2?')
      lock = False
      sio.emit('stage2_prompt_trigger')

  else:
    log('[ERR] Another operation is in progress.')
       
@sio.on('stage2_response_trigger')
def stage2_response_trigger(sid, answer):
  global lock
  if not lock:
    lock = True
    if answer is True:
      sio.start_background_task(sio.emit('stage2_start'))
      log('---------------------------------------')
      log('[STAGE 2] Stage 2 Starting...')
      log('[GPIO] Stirrer ON')
      GPIO.output(stirrer_pin, GPIO.LOW)
      log('[GPIO] Heater ON')
      GPIO.output(heater_pin, GPIO.LOW)

      log('[GPIO] Solenoid open for {0} seconds'.format(SOLENOID_TIMER))
      GPIO.output(solenoid_pin, GPIO.LOW)
      time.sleep(SOLENOID_TIMER)
      GPIO.output(solenoid_pin, GPIO.HIGH)

      log('[STAGE 2] Waiting for temperature to reach Stage 2 threshold ({0}deg Celcius)'.format(HEAT_THRESHOLD_2))

      while True:
        global temp_value
        temp_value = max6675.read_temp(temp_cs)
        sio.start_background_task(sio.emit('temp', temp_value))

        if temp_value >= HEAT_THRESHOLD_2:
          log("[STAGE 2] Temperature reached Stage 2 threshold.")
          break
        else:
          max6675.time.sleep(LOOP_INTERVALS)

      GPIO.output(heater_pin, GPIO.HIGH)
      log('[GPIO] Heater OFF')
      GPIO.output(stirrer_pin, GPIO.HIGH)
      log('[GPIO] Stirrer OFF')

      log('[STAGE 2] Process complete. Cleaning up and restarting...')
      time.sleep(2)
      lock = False
      restart()
    else:
      lock = False
      restart()

  else:
    log('[ERR] Another operation is in progress.')

# Serve the built React app files
@app.route('/')
def serve_client():
  return send_from_directory('client/build', 'index.html')

@app.route('/favicon.ico')
def serve_icon():
  return send_from_directory('client/build', 'favicon.ico')

@app.route('/static/<path:path>')
def serve_static(path):
  return send_from_directory('client/build/static', path)

@app.route('/static/js/<path:path>')
def serve_js(path):
  return send_from_directory('client/build/static/js', path)

@app.route('/static/css/<path:path>')
def serve_css(path):
  return send_from_directory('client/build/static/css', path)


# Start the server
if __name__ == '__main__':
    # eventlet.spawn(temperature_update)
    # wsgi_server_greenlet = eventlet.spawn(temperature_update)

    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
