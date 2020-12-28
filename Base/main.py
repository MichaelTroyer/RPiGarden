# -*- coding: utf-8 -*-
"""
Created 2020-10-26
@author: michael

main.py is the main program script.
main.py polls the DHT22 sensors, adjusts the garden environment, and logs the data.
"""

from datetime import datetime
import logging
import os
from time import sleep

import board

from database import Database
from peripherals import DHT_Sensor, Outlet
from reports import email_report


# Settings
# *Lights are controlled by a separate mechanical timer
# *Air Pumps (not detailed here) are on 24/7
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
            daytime = LIGHTS_ON < dateTime.time() < LIGHTS_OFF
            if daytime:
                min_temp, max_temp = DAY_MIN_TEMP, DAY_MAX_TEMP
            else:
                min_temp, max_temp = NIGHT_MIN_TEMP, NIGHT_MAX_TEMP

            # Read sensors
            ts, hs = [], []
            for sensor in sensors:
                try:
                    h, t = sensor.read()
                    # Filter bad data
                    if 0 < h < 100: hs.append(h)
                    if 0 < t < 100: ts.append(t)
                except:
                    msg = f'Error getting data from Sensor on pin {sensor.data_pin}'
                    print(msg); logging.error(msg)
                sleep(1)
            # This shouldn't happen unless a there's a bigger issue
            if not any(ts) or not any(hs): raise Exception('Total sensor failure..')
            # Average the results
            humidity = sum(hs) / len(hs)
            air_temperature = sum(ts) / len(ts)

            # Apply corrections
            humidity += HUMIDITY_CORRECTION
            air_temperature += TEMPERATURE_CORRECTION

            # Adjust garden environment
            if air_temperature < min_temp: heater.power_on()
            elif air_temperature >= max_temp: heater.power_off()
            sleep(1)  # JIC
            if humidity >= MAX_HUMIDITY: fan.power_on()
            elif humidity < MIN_HUMIDITY: fan.power_off()

            db.add_data({
                'DateTime': dateTime,
                'AirTemperature': air_temperature,
                'Humidity': humidity,
                'LightsOn': daytime,
                'HeaterOn': heater.power.value,
                'FanOn':fan.power.value,
                })

            print(
                f'Time: {dateTime.time().strftime("%H:%M:%S")} | '\
                f'Temp: {air_temperature:.3}f | '\
                f'RH: {humidity:.3}% | '\
                f'Lights: {"On" if daytime else "Off":>3} | '\
                f'Heater: {"On" if heater.power.value else "Off":>3} | '\
                f'Fan: {"On" if fan.power.value else "Off":>3}'
                )
            sleep(wait)

    except Exception as e:
        err_msg = "--- PiGarden Program Error ---"
        logging.error(err_msg, exc_info=True)
        print(f'{err_msg}\n{e}')
        email_report(
            email_add, passx,
            err_msg,
            f'Unhandled Exception:\n\n[{e}]\n\nSee attached logfile for more details..',
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
