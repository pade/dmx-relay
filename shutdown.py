#!/usr/bin/env python

import RPi.GPIO as GPIO
import subprocess

PIN = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(PIN, GPIO.FALLING)

subprocess.call(['shutdown', '-h', 'now'], shell=False)
