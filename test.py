#! /usr/bin/python3
# coding: utf8
import os
import time
import RPi.GPIO as GPIO

WIFI = True

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

def wifi_switch():
	global WIFI
	if WIFI:
		cmd = 'ifconfig wlan0 down'
		#os.system(cmd)
		WIFI = False
		GPIO.output(LED, GPIO.LOW)
	else:
		cmd = 'ifconfig wlan0 up'
		#os.system(cmd)
		WIFI = True
		while True:
			time.sleep(0.5)
			GPIO.output(LED, GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(LED, GPIO.LOW)

def button_callback(channel):
	print("Button pushed ! Switching wifi state...")
	wifi_switch()
	
if __name__ == "__main__":
	wifi_switch()
	GPIO.add_event_detect(BTN, GPIO.RISING, callback=button_callback)
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass    
	clean_all()
