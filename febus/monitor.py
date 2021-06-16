"""
Functions to take actions depending on the Febus server state.
"""

from __future__ import print_function

import time

from .cli import disable, enable, get_params, get_status, start, stop
from .parser import parse_gpstime_pulseid, parse_utcdatetime_blockid


def monitor(server):
    while True:
        line = server.stdout.readline()
        utcdatetime, block = parse_utcdatetime_blockid(line)
        if utcdatetime and block:
            print(utcdatetime, block)
        gpstime = parse_gpstime_pulseid(line)
        if gpstime:
            print(line)


def chunk(server, nblock):
    while True:
        line = server.stdout.readline()
        utcdatetime, blockid = parse_utcdatetime_blockid(line)
        if utcdatetime and blockid:
            if blockid % nblock == nblock - 1:
                print("disable")
                disable()
            if blockid % nblock == 0:
                print("enable")
                enable()
            print(utcdatetime, blockid)


def robust(params):  # TODO: use get_params instead
    while True:
        status = get_status()
        if not status == "running":
            disable()
            stop()
            enable()
            start(**params)
            time.sleep(1)
