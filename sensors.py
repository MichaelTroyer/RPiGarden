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


class DHT_Sensor(object):
    def __init__(self, data_pin, circuit_pin, device=adht.DHT22):
        self.data_pin = data_pin
        self.circuit_pin = circuit_pin
        self.device = device

        GPIO.setup(self.circuit_pin, GPIO.OUT)
        GPIO.output(self.circuit_pin, GPIO.LOW)

    def read(self):
        h, t = adht.read_retry(self.device, self.data_pin)
        if not (h and t):
            self.refresh()
            h, t = adht.read_retry(self.device, self.data_pin)
            if not (h and t):
                raise Exception('Sensor Error..')
        t = (t * 1.8) + 32
        return (h, t)

    def refresh(self):
        GPIO.output(self.circuit_pin, GPIO.HIGH)
        sleep(1)
        GPIO.output(self.circuit_pin, GPIO.LOW)


if __name__ == '__main__':
    s1 = DHT_Sensor(22, 23)
    s2 = DHT_Sensor(27, 17)
    while True:
        print(s1.read())
        print(s2.read())
        sleep(3)