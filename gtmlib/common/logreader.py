import json
import io
import os
import time


def show_log():
    """Helper method to show the gigantum log cleanly"""
    ffwd = 0
    logpath = os.path.expanduser('~/gigantum/.labmanager/logs/labmanager.log')

    with io.open(logpath, buffering=1) as f:
        while f.readline() != "":
            ffwd += 1
        print(f"Skipped {ffwd} records.")
        while True:
            l = f.readline()
            if l:
                d = json.loads(l)
                print(f"{d.get('levelname')} -- {d.get('filename')}::{d.get('funcName')}.{d.get('lineno')} -- {d.get('message')}")
            else:
                time.sleep(2)

