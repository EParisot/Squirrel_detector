#! /usr/bin/python3
# coding: utf8
import os
import time
from picamera import PiCamera
import adafruit_vl53l0x
import board
import busio
import RPi.GPIO as GPIO

DEBUG = False

if DEBUG:
	import logging
	from logging.handlers import RotatingFileHandler
	# setup logger
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

# images out folder
SRC_FOLDER = "/home/pi/Squirrel_detector/out/"
# images out extention
IMG_EXT = ".png"
# wifi state
WIFI = True
# distance trigger threshold
threshold = 45
# GPIOs pins
BTN = 12
BTNVCC = 13
LED = 5
LIGHT = 24

def init_dist_sensor():
	global threshold
	try:
		# init distance sensor
		i2c = busio.I2C(board.SCL, board.SDA)
		dist_sensor = adafruit_vl53l0x.VL53L0X(i2c)
		dist_sensor.measurement_timing_budget = 200000
		# define the average distance from i mesures
		thrs = []
		i = 5
		while i > 0:
			# blink led
			time.sleep(0.5)
			GPIO.output(LED, GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(LED, GPIO.LOW)
			# mesure and store distance
			distance = dist_sensor.range // 10
			if DEBUG:
				logger.debug("distance = %d" % distance)
			if 0 < distance < 50:
				thrs.append(distance)
			i -= 1
		# compute average distance
		if len(thrs):
			new_thr = sum(thrs) // len(thrs)
			if 0 < new_thr <= 50:
				threshold = new_thr
		if DEBUG:
			logger.debug("threshold = %d" % threshold)
	except Exception as e:
		if DEBUG:
			logger.info("Error setting dist sensor %s" % str(e))
	return dist_sensor

def init_GPIO():
	# GPIO setup
	GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(BTNVCC, GPIO.OUT)
	GPIO.output(BTNVCC, GPIO.HIGH)
	GPIO.setup(LED, GPIO.OUT)
	GPIO.output(LED, GPIO.LOW)

def light_sensor():
	count = 0
	# Output on the pin
	GPIO.setup(LIGHT, GPIO.OUT)
	GPIO.output(LIGHT, GPIO.LOW)
	time.sleep(0.1)
	# Change the pin back to input
	GPIO.setup(LIGHT, GPIO.IN)
	# Count until the pin goes high
	while (GPIO.input(LIGHT) == GPIO.LOW):
		count += 1
	return count

def clean_all():
	# setup wifi back
	cmd = 'ifconfig wlan0 up'
	os.system(cmd)
	time.sleep(1)
	# start wpa supplicant back
	cmd = "systemctl start wpa_supplicant@ap0.service"
	# cleanup GPIOs
	GPIO.output(LED, GPIO.LOW)
	GPIO.output(BTNVCC, GPIO.LOW)
	GPIO.cleanup()

def wifi_switch(WIFI):
	# setup wifi config from WIFI state
	if WIFI:
		if DEBUG:
			logger.info("Disactivate Wifi AP")
		cmd = "systemctl start wpa_supplicant@wlan0.service"
		os.system(cmd)
		time.sleep(1)
		cmd = 'ifconfig wlan0 down'
		os.system(cmd)
	else:
		if DEBUG:
			logger.info("Activate Wifi AP")
		cmd = 'ifconfig wlan0 up'
		os.system(cmd)
		time.sleep(1)
		cmd = "systemctl start wpa_supplicant@ap0.service"
		os.system(cmd)
	time.sleep(1)

def button_callback(channel):
	# avoid button bouncing
	time.sleep(0.1)
	if GPIO.input(BTN) == GPIO.LOW:
		return
	global WIFI, start_AP
	if DEBUG:
		logger.info("Button pushed ! Switching wifi state to %s" % ("OFF" if WIFI else "ON"))
	# switch wifi state
	wifi_switch(WIFI)
	if WIFI:
		start_AP = None
	WIFI = not WIFI

def take_snap():
	# take picture and save it
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
	# blink led 3s to confirm test image is taken
	GPIO.output(LED, GPIO.HIGH)
	time.sleep(3)
	GPIO.output(LED, GPIO.LOW)

if __name__ == "__main__":
	if DEBUG:
		logger.info("SQRT Started...")
	# init dist sensor, button and wifi
	init_GPIO()
	dist_sensor = init_dist_sensor()
	wifi_switch(WIFI)
	WIFI = False
	GPIO.add_event_detect(BTN, GPIO.RISING, callback=button_callback)
	start_AP = None
	try:
		# avoid camera bugs by testing on start
		test_snap()
		# main loop
		while True:
			# get light level
			light = light_sensor()
			if DEBUG:
				logger.debug("Light level = %d" % light)
			# avoid looping if light id too low to save power
			if not WIFI and light > 10000:
				time.sleep(60 * 10)
				continue
			if WIFI:
				# blink the led if wifi is ON
				time.sleep(0.5)
				GPIO.output(LED, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(LED, GPIO.LOW)
				# start AccesPoint or wait for timer to elapse... (15 min)
				if start_AP == None:
					start_AP = time.time()
				elif time.time() - start_AP >= 60 * 15:
					start_AP = None
					wifi_switch(WIFI)
					WIFI = False
				if DEBUG:
					distance = dist_sensor.range // 10
					logger.debug("distance = %d" % distance)
			else:
				# stop the led
				GPIO.output(LED, GPIO.LOW)
				time.sleep(1)
				# mseure distance
				distance = dist_sensor.range // 10
				if DEBUG:
					logger.debug("distance = %d" % distance)
				# take snap if distance have changed
				if distance > 0 and distance < threshold:
					if DEBUG:
						logger.debug("SNAP")
					take_snap()
	except Exception as e:
		if DEBUG:
			logger.debug(str(e))
	clean_all()
