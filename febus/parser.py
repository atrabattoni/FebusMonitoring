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


def parse_walltime(line):
    """Get the loop wall time"""
    pattern = r"\[SERVER\] cuda block wall clock (?P<walltime>\d*\.?\d*)"
    m = re.match(pattern, line)
    if m is not None:
        walltime = round(float(m.group("walltime")), 3)
        return walltime
    else:
        return None


def parse_gpstime_pulseid(line):
    """Get the GPS time information and corresponding pulse ID"""
    pattern = r"CoProcess ref pulseID: (?P<pulseid>\d+) timestamp:(?P<timestamp>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = round(float(m.group("timestamp")), 3)
        gpstime = datetime.datetime.utcfromtimestamp(timestamp)
        pulseid = int(m.group("pulseid"))
        return gpstime, pulseid
    else:
        return None, None


def parse_trigid(line):
    """Get the trigid information"""
    pattern = r"CoProcess trigid: (?P<trigid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        trigid = int(m.group("trigid"))
        return trigid
    else:
        return None


def parse_utcdatetime_blockid(line):
    """Get the UTC datetime and ID of each block"""
    pattern = r"\t\t\tCoProcessing (?P<blockid>\d+) \d*\.?\d* \|realtime: (?P<timestamp>\d*\.?\d*)\| \d*\.?\d* -?\d*\.?\d*"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = round(float(m.group("timestamp")), 3)
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)
        blockid = int(m.group("blockid"))
        return utcdatetime, blockid
    else:
        return None, None


def parse_writetime(line):
    """Get the block write time"""
    pattern = r"\[HDF5Writer\]\[Info\] Writing data took (?P<writetime>\d*\.?\d*) ms"
    m = re.match(pattern, line)
    if m is not None:
        writetime = round(float(m.group("writetime")) / 1000, 3)
        return writetime
    else:
        return None


def parse_coprocessingtime(line):
    """Get the block write time"""
    pattern = r"###Coprocessing took (?P<coprocessingtime>\d*\.?\d*) \(seconds\)"
    m = re.match(pattern, line)
    if m is not None:
        coprocessingtime = round(float(m.group("coprocessingtime")), 3)
        return coprocessingtime
    else:
        return None
