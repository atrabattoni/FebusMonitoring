from __future__ import print_function

from .parser import parse_utcdatetime_blockid, parse_gpstime_pulseid
from .cli import enable, disable

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
        if blockid % nblock == 0:
            disable()
        if blockid % nblock == 1:
            enable()
