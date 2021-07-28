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


def parse_new_loop(line):
    """Find start of loop"""
    return line == "New loop \n"


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


def parse_wall_time(line):
    """Get the loop wall time"""
    pattern = r"\[SERVER\] cuda block wall clock (?P<wall_time>\d+\.\d+)"
    m = re.match(pattern, line)
    if m is not None:
        wall_time = float(m.group("wall_time"))
        return wall_time
    else:
        return None


def parse_trigid(line):
    """Get the trigid information"""
    pattern = r"CoProcess trigid: (?P<trigid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        trigid = float(m.group("trigid"))
        return trigid
    else:
        return None


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


def parse_write_time(line):
    """Get the block write time"""
    pattern = r"[HDF5Writer][Info] Writing data took (?P<write_time>\d+\.\d+) ms"
    m = re.match(pattern, line)
    if m is not None:
        write_time = float(m.group("write_time"))
        return write_time
    else:
        return None


def parse_coprocessing_time(line):
    """Get the block write time"""
    pattern = r"###Coprocessing took (?P<coprocessing_time>\d+\.\d+) (seconds)"
    m = re.match(pattern, line)
    if m is not None:
        coprocessing_time = float(m.group("coprocessing_time"))
        return coprocessing_time
    else:
        return None
