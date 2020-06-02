import subprocess
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import logging

from logging.handler import RotatingFileHandler

logger = logging.GetLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

GPIO.setmode(GPIO.BCM)

Trig = 23          # Trig HC-SR04 GPIO 23
Echo = 24          # Echo HC-SR04 GPIO 24

GPIO.setup(Trig,GPIO.OUT)
GPIO.setup(Echo,GPIO.IN)

GPIO.output(Trig, False)

threshold = 49
wifi_timeout = 30
start_time = time.time()
wifi_state = True

def take_snap():
    with PiCamera() as camera:
        filename = "out/" + str(time.time()) + ".png"
        logger.info("captured %s" % filename)
        camera.capture(filename)

def stop_wifi():
    res = subprocess.check_output("ip a | grep wlan0 | grep state", shell=True)
    if str(res).split("state ")[1][:2] != "UP":
        logger.info("shuting down wifi...")
        

try:
    while True:

       time.sleep(1)

       GPIO.output(Trig, True)
       time.sleep(0.00001)
       GPIO.output(Trig, False)

       while GPIO.input(Echo)==0:   ## ultrasonic emit
         startImpulse = time.time()

       while GPIO.input(Echo)==1:   ## echo back
         endImpulse = time.time()

       distance = round((endImpulse - startImpulse) * 340 * 100 / 2, 1)  ## speed of sound = 340 m/s
       
       if distance < threshold:
           take_snap()
      
      if time.time() > start_time and wifi_state == True:
          stop_wifi()
          wifi_state = False


except KeyboardInterrupt:
    pass

GPIO.cleanup()
