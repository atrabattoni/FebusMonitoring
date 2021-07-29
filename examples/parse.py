"""
Offline parsing of some terminal logs.
"""

import datetime
from febus.parser import parse_blocktime_block, parse_pulsetime_pulseid

fname = "path_to_log"  # to change by the user

verbose = False
count = 0
errorline = 0
line = True
with open(fname, "r") as server:  # the file simulate the server
    while line:
        line = server.readline()
        blocktime, blockid = parse_blocktime_block(line)
        if blocktime and blockid:
            if blocktime > datetime.datetime(3100, 1, 1):
                verbose = True
                errorline = count
            if verbose:
                print("Loop:", blocktime, blockid)
        pulsetime, pulseid = parse_pulsetime_pulseid(line)
        if pulsetime and pulseid:
            if pulsetime > datetime.datetime(3100, 1, 1):
                verbose = True
                errorline = count
            if verbose:
                print()
                print("GPS:", pulsetime, pulseid)
                print()
        count += 1
        if verbose and count - errorline > 1000:
            break
