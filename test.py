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
	GPIO.setmode(GPIO.BCM)
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
	else:
		cmd = 'ifconfig wlan0 up'
		os.system(cmd)

def button_callback(channel):
	print("Button pushed ! Switching wifi state...")
	global WIFI
	wifi_switch(WIFI)
	WIFI = not WIFI
	
if __name__ == "__main__":
	init_GPIO()
	wifi_switch(WIFI)
	WIFI = False
	GPIO.add_event_detect(BTN, GPIO.RISING, callback=button_callback)
	try:
		while True:
			if WIFI:
				time.sleep(0.25)
				GPIO.output(LED, GPIO.HIGH)
				time.sleep(0.25)
				GPIO.output(LED, GPIO.LOW)
			else:
				GPIO.output(LED, GPIO.LOW)
				time.sleep(1)
	except KeyboardInterrupt:
		pass    
	clean_all()
