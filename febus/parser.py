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


def parse_newloop(line):
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


def parse_pulse(line):
    """Get the reference time information and corresponding pulse ID"""
    pattern = r"CoProcess ref pulseID: (?P<pulseid>\d+) timestamp:(?P<pulsetime>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        pulseid = int(m.group("pulseid"))
        pulsetime = int(m.group("pulsetime"))
        pulsetime = datetime.datetime.utcfromtimestamp(pulsetime)
        return pulseid, pulsetime
    else:
        return None, None


def parse_trigger(line):
    """Get the trigger information"""
    pattern = r"CoProcess trigid: (?P<trigid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        trigid = int(m.group("trigid"))
        return trigid
    else:
        return None


def parse_block(line):
    """Get the UTC datetime and ID of each block"""
    pattern = r"\t\t\tCoProcessing (?P<blockid>\d+) (?P<blocktime>\d*\.?\d*) \|realtime: (?P<realtime>\d*\.?\d*)\| \d*\.?\d* -?\d*\.?\d*"
    m = re.match(pattern, line)
    if m is not None:
        blockid = int(m.group("blockid"))
        blocktime = float(m.group("blocktime"))
        realtime = float(m.group("realtime"))
        blocktime = datetime.datetime.utcfromtimestamp(blocktime)
        realtime = datetime.datetime.utcfromtimestamp(realtime)
        return blockid, blocktime, realtime
    else:
        return None, None, None


def parse_writing(line):
    """Get the block write time"""
    pattern = r"\[HDF5Writer\]\[Info\] Writing data took (?P<writingtime>\d*\.?\d*) ms"
    m = re.match(pattern, line)
    if m is not None:
        writingtime = round(float(m.group("writingtime")) / 1000, 3)
        return writingtime
    else:
        return None


def parse_coprocessing(line):
    """Get the block write time"""
    pattern = r"###Coprocessing took (?P<coprocessingtime>\d*\.?\d*) \(seconds\)"
    m = re.match(pattern, line)
    if m is not None:
        coprocessingtime = round(float(m.group("coprocessingtime")), 3)
        return coprocessingtime
    else:
        return None
