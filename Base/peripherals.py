# -*- coding: utf-8 -*-
"""
Created on 2020-10-26
@author: michael
"""

from time import sleep

import Adafruit_DHT as adht
import board
from digitalio import DigitalInOut, Direction
import RPi.GPIO as GPIO


# Settings
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class DHT_Sensor(object):
    '''
    DHT22 sensors are prone to hang-ups. A simple restart solves the problem.
    The sensor class requires a data_pin for measurements and a circuit pin
    that references the control GPIO pin on a seperate power relay that is used
    to switch the sensor off and back on.
    '''
    def __init__(self, data_pin, circuit_pin, device=adht.DHT22):
        self.data_pin = data_pin
        self.circuit_pin = circuit_pin
        self.device = device

        GPIO.setup(self.circuit_pin, GPIO.OUT)
        GPIO.output(self.circuit_pin, GPIO.LOW)

    def read(self):
        h, t = adht.read_retry(self.device, self.data_pin)
        if not (h and t):
            # if the sensor hangs, restart and try again.
            self.refresh()
            h, t = adht.read_retry(self.device, self.data_pin)
            if not (h and t):
                # if that didn't work, there's a bigger problem.
                raise Exception('Sensor Error..')
        t = (t * 1.8) + 32
        return (h, t)

    def refresh(self):
        # Make sure you get the GPIO HIGH/LOW status right for switch configuration
        GPIO.output(self.circuit_pin, GPIO.HIGH)
        sleep(1)
        GPIO.output(self.circuit_pin, GPIO.LOW)


class Outlet():
    '''
    3.3v switchable power relay:
    e.g. https://www.adafruit.com/product/2935
    '''
    def __init__(self, pin):
        self.pin = pin
        self.power = DigitalInOut(self.pin)
        self.power.direction = Direction.OUTPUT
        self.power.value = False

    def power_on(self):
        if not self.power.value:
            self.power.value = True

    def power_off(self):
        if self.power.value:
            self.power.value = False


if __name__ == '__main__':
    sensors = [DHT_Sensor(22, 23), DHT_Sensor(27, 17)]
    while True:
        for sensor in sensors:
            print(sensor.read())
            sleep(3)