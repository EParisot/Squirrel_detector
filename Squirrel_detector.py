#! /usr/bin/python3
# coding: utf8
import os
import time
from picamera import PiCamera
import adafruit_vl53l0x
import board
import busio
import RPi.GPIO as GPIO

DEBUG = True

if DEBUG:
	import logging
	from logging.handlers import RotatingFileHandler

	logger = logging.getLogger("main_logger")
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.DEBUG)
	logger.addHandler(stream_handler)

SRC_FOLDER = "/home/pi/Squirrel_Detector/out/"
IMG_EXT = ".png"
WIFI = True
threshold = 45

def init_sensor():
	i2c = busio.I2C(board.SCL, board.SDA)
	sensor = adafruit_vl53l0x.VL53L0X(i2c)
	sensor.measurement_timing_budget = 200000
	return sensor

BTN = 12
BTNVCC = 13
LED = 5
def init_GPIO():
	GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(BTNVCC, GPIO.OUT)
	GPIO.output(BTNVCC, GPIO.HIGH)
	GPIO.setup(LED, GPIO.OUT)
	GPIO.output(LED, GPIO.LOW)

def clean_all():
	GPIO.output(LED, GPIO.LOW)
	GPIO.output(BTNVCC, GPIO.LOW)
	GPIO.cleanup()

def wifi_switch(WIFI):
	if WIFI:
		cmd = 'ifconfig wlan0 down'
		os.system(cmd)
		time.sleep(1)
		cmd = "systemctl start wpa_supplicant@wlan0.service"
		os.system(cmd)
	else:
		cmd = 'ifconfig wlan0 up'
		os.system(cmd)
		time.sleep(1)
		cmd = "systemctl start wpa_supplicant@ap0.service"
		os.system(cmd)
	time.sleep(1)

def button_callback(channel):
	global WIFI
	if DEBUG:
		logger.info("Button pushed ! Switching wifi state to %s" % ("OFF" if WIFI else "ON"))
	wifi_switch(WIFI)
	WIFI = not WIFI
	
def take_snap():
	with PiCamera(resolution=(1920, 1080)) as camera:
		camera.rotation = 180
		filename = SRC_FOLDER + str(time.time()) + IMG_EXT
		if DEBUG:
			logger.info("captured %s" % filename)
		camera.capture(filename)

def test_snap():
	try:
		take_snap()
	except Exception as e:
		if DEBUG:
			logger.debug(str(e))
		clean_all()
		exit()

if __name__ == "__main__":
	init_GPIO()
	sensor = init_sensor()
	wifi_switch(WIFI)
	WIFI = False
	GPIO.add_event_detect(BTN, GPIO.RISING, callback=button_callback)
	try:
		test_snap()
		while True:
			if WIFI:
				time.sleep(0.5)
				GPIO.output(LED, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(LED, GPIO.LOW)
			else:
				GPIO.output(LED, GPIO.LOW)
				time.sleep(1)
				distance = sensor.range // 10
				if distance > 0 and distance < threshold:
					take_snap()
	except Exception as e:
		if DEBUG:
			logger.debug(str(e))
	clean_all()