"""
Functions to extract relevant information in the server logs.
"""

import datetime
import re


def parse_error(line):
    """Search for errors"""
    s = re.search(r"error", line, re.IGNORECASE)
    if s is not None:
        return True


def parse_utcdatetime_blockid(line):
    """Get the UTC datetime and ID of each block"""
    pattern = r"\[CATALYST\] Calling pipeline on block (?P<timestamp>\d+)\.\d+ (?P<blockid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = float(m.group("timestamp"))
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)
        blockid = int(m.group("blockid"))
        return utcdatetime, blockid
    else:
        return None, None


def parse_gpstime_pulseid(line):
    """Get the GPS time information and corresponding pulse ID"""
    pattern = r"GENEPULSE Sending TimeStamp:(?P<timestamp>\d+).+PulseID:(?P<pulseid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = float(m.group("timestamp"))
        gpstime = datetime.datetime.utcfromtimestamp(timestamp)
        pulseid = int(m.group("pulseid"))
        return gpstime, pulseid
    else:
        return None, None


def parse_new_loop(line):
    """Find start of loop"""
    return line == "New loop \n"
