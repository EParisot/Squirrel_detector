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

SRC_FOLDER = "/home/pi/Squirrel_detector/out/"
IMG_EXT = ".png"
WIFI = True
threshold = 45
BTN = 12
LED = 5
LIGHT = 24

def init_sensor():
	global threshold
	try:
		i2c = busio.I2C(board.SCL, board.SDA)
		sensor = adafruit_vl53l0x.VL53L0X(i2c)
		sensor.measurement_timing_budget = 200000
		thrs = []
		i = 5
		while i > 0:
			time.sleep(0.5)
			GPIO.output(LED, GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(LED, GPIO.LOW)
			distance = sensor.range // 10
			if DEBUG:
				logger.debug("distance = %d" % distance)
			if 0 < distance < 50:
				thrs.append(distance)
			i -= 1
		if len(thrs):
			new_thr = sum(thrs) // len(thrs)
			if 0 < new_thr <= 50:
				threshold = new_thr
		if DEBUG:
			logger.debug("threshold = %d" % threshold)
	except Exception as e:
		if DEBUG:
			logger.info("Error setting dist sensor %s" % str(e))
	return sensor

def init_GPIO():
	GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(LED, GPIO.OUT)
	GPIO.output(LED, GPIO.LOW)

def light_sensor():
	count = 0
	#Output on the pin for
	GPIO.setup(LIGHT, GPIO.OUT)
	GPIO.output(LIGHT, GPIO.LOW)
	time.sleep(0.1)
	#Change the pin back to input
	GPIO.setup(LIGHT, GPIO.IN)
	#Count until the pin goes high
	while (GPIO.input(LIGHT) == GPIO.LOW):
		count += 1
	return count

def clean_all():
	cmd = 'ifconfig wlan0 up'
	os.system(cmd)
	time.sleep(1)
	cmd = "systemctl start wpa_supplicant@ap0.service"
	GPIO.output(LED, GPIO.LOW)
	GPIO.cleanup()

def wifi_switch():
	global start_AP
	if WIFI == False:
		if DEBUG:
			logger.info("Disactivate Wifi AP")
		cmd = "systemctl start wpa_supplicant@wlan0.service"
		os.system(cmd)
		time.sleep(1)
		cmd = 'ifconfig wlan0 down'
		os.system(cmd)
	elif WIFI == True:
		if DEBUG:
			logger.info("Activate Wifi AP")
		cmd = 'ifconfig wlan0 up'
		os.system(cmd)
		time.sleep(1)
		cmd = "systemctl start wpa_supplicant@ap0.service"
		os.system(cmd)
		start_AP = time.time()
	time.sleep(1)

def button_callback(channel):
	if GPIO.input(BTN) == 0:
		global WIFI
		if DEBUG:
			logger.info("Button pushed ! Switching wifi state to %s" % ("OFF" if WIFI else "ON"))
		WIFI = not WIFI
		wifi_switch()

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
	GPIO.output(LED, GPIO.HIGH)
	time.sleep(3)
	GPIO.output(LED, GPIO.LOW)

if __name__ == "__main__":
	if DEBUG:
		logger.info("SQRT Started...")
	init_GPIO()
	sensor = init_sensor()
	WIFI = False
	start_AP = None
	wifi_switch()
	GPIO.add_event_detect(BTN, GPIO.FALLING, callback=button_callback, bouncetime=500)
	try:
		test_snap()
		while True:
			"""light = light_sensor()
			if DEBUG:
				logger.debug("Light level = %d" % light)
			if not WIFI and light > 10000:
				time.sleep(60 * 10)
				continue"""
			if WIFI == True:
				time.sleep(0.5)
				GPIO.output(LED, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(LED, GPIO.LOW)
				if start_AP != None and time.time() - start_AP >= 60 * 15:
					start_AP = None
					wifi_switch()
					WIFI = False
				if DEBUG:
					distance = sensor.range // 10
					logger.debug("distance = %d" % distance)
			else:
				GPIO.output(LED, GPIO.LOW)
				time.sleep(1)
				distance = sensor.range // 10
				if DEBUG:
					logger.debug("distance = %d" % distance)
				if distance > 0 and distance < threshold:
					if DEBUG:
						logger.debug("SNAP")
					take_snap()
	except Exception as e:
		if DEBUG:
			logger.debug(str(e))
	clean_all()
