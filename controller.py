# -*- coding: utf-8 -*-
"""
Created 2020-10-26
@author: michael
"""

from subprocess import Popen

filename = 'main.py'
MAX_RETRIES = 10

retry = 0

while retry <= MAX_RETRIES:
    try:
        print(f'Starting Process: {filename}')
        p = Popen(f'python {filename}', shell=True)
        p.wait()
    except Exception as e:
        print(e)
    finally:
        try:
            p.terminate()
        except: pass
        retries += 1