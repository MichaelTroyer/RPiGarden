# -*- coding: utf-8 -*-
"""
Created 2020-10-26
@author: michael
"""

import time

import board
from digitalio import DigitalInOut, Direction


class Outlet():
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

    