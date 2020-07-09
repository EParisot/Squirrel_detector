import time
from picamera import PiCamera
import board
import busio
import adafruit_vl53l0x
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)
sensor.measurement_timing_budget = 200000

SRC_FOLDER = "out/"
IMG_EXT = ".png"

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

threshold = 45

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
		exit()

if __name__ == "__main__":
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
