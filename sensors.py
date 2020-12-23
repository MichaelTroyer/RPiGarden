# -*- coding: utf-8 -*-
"""
Created on 2020-10-26
@author: michael
"""

from time import sleep

import RPi.GPIO as GPIO
import Adafruit_DHT as adht


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def get_temp_and_humidity(device=adht.DHT22, pin=17):
    return adht.read_retry(device, pin)


if __name__ == '__main__':
    while True:
        h, t = get_temp_and_humidity()
        t = (t * 1.8) + 32
        print(f'temp: {t:.4}, humidity; {h:.4}')
        sleep(5)