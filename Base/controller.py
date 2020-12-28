# -*- coding: utf-8 -*-
"""
Created 2020-12-26
@author: michael


controller.py is called by an @reboot cron job on the Raspberry Pi so it auto starts on boot.

controller.py manages the main program script by calling it within a subprocess
and handling potential exceptions with a fixed number of retries.

*The main.py script handles the email error reporting for failures.
"""


from subprocess import Popen


FILENAME = 'main.py'
MAX_RETRIES = 10


retry = 0
while retry < MAX_RETRIES:
    try:
        print(f'Starting Process: {filename}')
        p = Popen(f'python {filename}', shell=True)
        p.wait()
    except Exception as e:
        print(e)
    finally:
        retry += 1
        try:
            p.terminate()
        except:
            pass
