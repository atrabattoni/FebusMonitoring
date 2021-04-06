from __future__ import print_function

from .parser import parse_utcdatetime_block, parse_gpstime

def monitor(server):
    while True:
        line = server.stdout.readline()
        utcdatetime, block = parse_utcdatetime_block(line)
        if utcdatetime and block:
            print(utcdatetime, block)
        gpstime = parse_gpstime(line)
        if gpstime:
            print(line)
