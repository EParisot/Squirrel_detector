#! /usr/bin/python3
# coding: utf8

import time
from picamera import PiCamera
import board
import busio
import adafruit_vl53l0x
import RPi.GPIO as GPIO
import threading

from BLT_server.bltServer import run_server

DEBUG = True

if DEBUG:
	import logging
	from logging.handlers import RotatingFileHandler

	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.DEBUG)
	logger.addHandler(stream_handler)

SRC_FOLDER = "out/"
IMG_EXT = ".png"

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

def button_callback(channel):
	if DEBUG:
		logger.info("Button was pushed!")
	blt_t = threading.Thread(target=run_server)
	blt_t.start()
	if DEBUG:
		logger.info("Waiting for threads ton complete")
	while blt_t.is_alive():
		time.sleep(0.5)
		GPIO.output(LED, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(LED, GPIO.LOW)
	
def take_snap():
	with PiCamera(resolution=(1920, 1080)) as camera:
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
	sensor = init_sensor()
	init_GPIO()
	GPIO.add_event_detect(BTN, GPIO.RISING, callback=button_callback)
	try:
		test_snap()
		while True:
			time.sleep(1)
			distance = sensor.range // 10
			if DEBUG:
				logger.debug(distance)
			if distance > 0 and distance < threshold:
				take_snap()
	except Exception as e:
		if DEBUG:
			logger.debug(str(e))
	clean_all()
