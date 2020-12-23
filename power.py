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
        self.power.value = True

    def power_off(self):
        self.power.value = False

    