"""
Offline parsing of some terminal logs.
"""

from __future__ import print_function

import datetime
from febus.parser import parse_utcdatetime_block, parse_gpstime_pulseid

fname = "path_to_log"  # to change by the user

verbose = False
count = 0
errorline = 0
line = True
with open(fname, "r") as server:  # the file simulate the server
    while line:
        line = server.readline()
        utcdatetime, blockid = parse_utcdatetime_block(line)
        if utcdatetime and blockid:
            if utcdatetime > datetime.datetime(3100, 1, 1):
                verbose = True
                errorline = count
            if verbose:
                print("Loop:", utcdatetime, blockid)
        gpstime, pulseid = parse_gpstime_pulseid(line)
        if gpstime and pulseid:
            if gpstime > datetime.datetime(3100, 1, 1):
                verbose = True
                errorline = count
            if verbose:
                print()
                print("GPS:", gpstime, pulseid)
                print()
        count += 1
        if verbose and count - errorline > 1000:
            break
