from __future__ import print_function

import datetime
import re


def parse_error(line):
    """Search for errors"""
    s = re.search(r"error", line, re.IGNORECASE)
    if s is not None:
        return True


def parse_utcdatetime_block(line):
    """Get the UTC datetime of each block"""
    pattern = r"\[CATALYST\] Calling pipeline on block (?P<timestamp>\d+)\.\d+ (?P<block>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = float(m.group("timestamp"))
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)
        block = int(m.group("block"))
        return utcdatetime, block
    else:
        return None, None


def parse_gpstime(line):
    """Get the GPS time information"""
    pattern = r"GENEPULSE Sending TimeStamp"
    m = re.match(pattern, line)
    return m
