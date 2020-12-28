# -*- coding: utf-8 -*-
"""
Created 2020-10-26
@author: michael
"""

import os
import logging

from datetime import datetime
from time import sleep

import board

from database import Database
from power import Outlet
from report import email_report
from sensors import DHT_Sensor


# Settings
LIGHTS_ON = datetime.strptime('07:30', "%H:%M").time()
LIGHTS_OFF = datetime.strptime('22:00', "%H:%M").time()

DAY_MAX_TEMP = 81.0
DAY_MIN_TEMP = 76.0
NIGHT_MAX_TEMP = 78.0
NIGHT_MIN_TEMP = 73.0

MAX_HUMIDITY = 60.0
MIN_HUMIDITY = 40.0

HUMIDITY_CORRECTION = -4.0  # Percent RH
TEMPERATURE_CORRECTION = 0.0  # Degrees C


def main(database, logfile, email_add, passx, wait=30):
    # Logfile
    logging.basicConfig(
            filename=logfile,
            filemode='a',
            format='%(asctime)s - %(message)s',
            level=logging.INFO
            )
    logging.info(f'Reporting to: {email_add}')

    # Database
    db = Database(database)

    # Outlets
    heater = Outlet(pin=board.D26)
    fan = Outlet(pin=board.D24)

    # Sensors
    sensor_1 = DHT_Sensor(data_pin=27, circuit_pin=17)
    sensor_2 = DHT_Sensor(data_pin=22, circuit_pin=23)
    sensors = [sensor_1, sensor_2]

    try:       
        while True:
            dateTime = datetime.now()
            if LIGHTS_ON < dateTime.time() < LIGHTS_OFF:
                min_temp, max_temp = DAY_MIN_TEMP, DAY_MAX_TEMP
            else:
                min_temp, max_temp = NIGHT_MIN_TEMP, NIGHT_MAX_TEMP

            # Read sensors
            ts, hs = [], []
            for sensor in sensors:
                try:
                    h, t = sensor.read()
                    if 0 < h < 100: hs.append(h)
                    if 0 < t < 100: ts.append(t)
                except:
                    msg = f'Error getting data from Sensor on pin {sensor.data_pin}'
                    print(msg); logging.error(msg)
                sleep(1)
            if not any(ts) or not any(hs): raise Exception('Total sensor failure..')
            humidity = sum(hs) / len(hs)
            air_temperature = sum(ts) / len(ts)
            
            # Apply corrections
            humidity += HUMIDITY_CORRECTION
            air_temperature += TEMPERATURE_CORRECTION

            # Adjust garden environment
            if air_temperature < min_temp: heater.power_on()
            elif air_temperature >= max_temp: heater.power_off()
            if humidity >= MAX_HUMIDITY: fan.power_on()
            elif humidity < MIN_HUMIDITY: fan.power_off()

            db.add_data({
                'DateTime': dateTime,
                'AirTemperature': air_temperature,
                'Humidity': humidity,
                'HeaterOn': heater.power.value,
                'FanOn':fan.power.value,
                })

            print(
                f'Time: {dateTime.time().strftime("%H:%M:%S")} | '\
                f'Temp: {air_temperature:.3}f | '\
                f'Humidity: {humidity:.3}% | '\
                f'Heater: {"On" if heater.power.value else "Off":>3} | '\
                f'Fan: {"On" if fan.power.value else "Off":>3}'
                )
            sleep(wait)

    except Exception as e:
        err_msg = "---PiGarden: Fatal Program Error---"
        logging.error(err_msg, exc_info=True)
        print(err_msg, e)
        email_report(
            email_add, passx, err_msg,
            f'Unhandled Exception:\n[{e}]\nSee attached logfile for more details..',
            atts=[logfile],
            )
    finally:
        import RPi.GPIO; RPi.GPIO.cleanup()


if __name__ == '__main__':
    import yaml

    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    database = os.path.join(root, 'Data', 'Garden.db')
    logfile = os.path.join(root, 'Logs', 'Garden.txt')
    yamlfile = os.path.join(root, 'Base', 'config', 'config.yaml')

    with open(yamlfile) as f:
        credentials = yaml.safe_load(f)

    main(database, logfile, credentials['Email'], credentials['Password'])
