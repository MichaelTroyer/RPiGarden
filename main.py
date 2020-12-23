# -*- coding: utf-8 -*-
import os
import logging
import yaml

from datetime import datetime
from time import sleep

import board

from database import Database
from power import Outlet
from report import email_report
from sensors import get_temp_and_humidity


LIGHTS_ON = datetime.strptime('07:30', "%H:%M").time()
LIGHTS_OFF = datetime.strptime('22:00', "%H:%M").time()

DAY_MAX_TEMP = 85.0
DAY_MIN_TEMP = 78.0
NIGHT_MAX_TEMP = 80.0
NIGHT_MIN_TEMP = 73.0

MAX_HUMIDITY = 65.0

HUMIDITY_CORRECTION = -5  # Percent RH
TEMPERATURE_CORRECTION = -1  # Degrees C


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

    try:       
        while True:
            dateTime = datetime.now()
            if LIGHTS_ON < dateTime.time() < LIGHTS_OFF:
                min_temp, max_temp  = DAY_MIN_TEMP, DAY_MAX_TEMP
            else:
                min_temp, max_temp  = NIGHT_MIN_TEMP, NIGHT_MAX_TEMP

            humidity, air_temperature = get_temp_and_humidity()

            # Corrections
            humidity += HUMIDITY_CORRECTION
            air_temperature += TEMPERATURE_CORRECTION
               
            air_temperature = (air_temperature * 1.8) + 32
            print(f'Time: {dateTime.time()} | Temp: {air_temperature:.4}f | Humidity: {humidity:.4}%')

            if air_temperature < min_temp:
                if not heater.power.value:
                    print('Temperature too low - Heater on..')
                    heater.power_on()
            elif air_temperature >= max_temp:
                if heater.power.value:
                    print('Temperature too high - Heater off..')
                    heater.power_off()

            if humidity >= MAX_HUMIDITY:
                if not fan.power.value:
                    print('Humidity too high - Fan on..')
                    fan.power_on()
            elif fan.power.value:
                print('Fan off..')
                fan.power_off()

            db.add_data({
                'DateTime': dateTime,
                'AirTemperature': air_temperature,
                'Humidity': humidity,
                'HeaterOn': heater.power.value,
                'FanOn':fan.power.value,
                })
            sleep(wait)

    except Exception as e:
        print(e)
        err_msg = "---UNHANDLED EXCEPTION - PROGRAM EXIT---"
        logging.error(err_msg, exc_info=True); print(err_msg)
        email_report(
            email_add, passx,
            'PiGarden Error!',
            f'Unhandled Exception:\n[{e}]\nSee attached logfile for more details..',
            atts=[logfile],
            )


if __name__ == '__main__':

    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    database = os.path.join(root, 'Data', 'Garden.db')
    logfile = os.path.join(root, 'Logs', 'Garden.txt')
    yamlfile = os.path.join(root, 'Base', 'config', 'config.yaml')

    with open(yamlfile) as f:
        credentials = yaml.safe_load(f)

    main(database, logfile, credentials['Email'], credentials['Password'])
