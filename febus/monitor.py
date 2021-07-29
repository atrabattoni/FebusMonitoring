"""
Functions to take actions depending on the Febus server state.
"""

import time

from .cli import disable, enable, get_params, get_status, start, stop
from .parser import parse_pulsetime_pulseid, parse_blocktime_blockid


def monitor(server):
    """Print server info"""
    while True:
        line = server.stdout.readline()
        blocktime, block = parse_blocktime_blockid(line)
        if blocktime and block:
            print(blocktime, block)
        pulsetime = parse_pulsetime_pulseid(line)
        if pulsetime:
            print(line)


def chunk(server, nblock):
    """Write smaller files by en/disabling HDF5 writing"""
    while True:
        line = server.stdout.readline()
        blocktime, blockid = parse_blocktime_blockid(line)
        if blocktime and blockid:
            if blockid % nblock == nblock - 1:
                print("disable")
                disable()
            if blockid % nblock == 0:
                print("enable")
                enable()
            print(blocktime, blockid)


def robust(params):
    """Robust aquisition that auto-restart if needed"""
    while True:
        status = get_status()
        if not status == "running":
            disable()
            stop()
            enable()
            start(**params)
            time.sleep(1)
