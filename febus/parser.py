import datetime
import re


def parse(line):
    parsers = [parse_newloop, parse_walltime, parse_pulse, parse_trigger,
               parse_block, parse_writing, parse_coprocessing, parse_timeout,
               parse_ready, parse_error]
    out = {}
    for parser in parsers:
        out.update(parser(line))
    return out


def parse_error(line):
    s = re.search(r"error", line, re.IGNORECASE)
    if s is not None:
        return {"error": True}
    else:
        return {}


def parse_newloop(line):
    if "New loop" in line:
        return {"newloop": True}
    else:
        return {}


def parse_walltime(line):
    pattern = r"\[SERVER\] cuda block wall clock (?P<walltime>\d*\.?\d*)"
    m = re.match(pattern, line)
    if m is not None:
        walltime = round(float(m.group("walltime")), 3)
        return {"walltime": walltime}
    else:
        return {}


def parse_pulse(line):
    pattern = r"CoProcess ref pulseID: (?P<pulseid>\d+) timestamp:(?P<pulsetime>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        pulseid = int(m.group("pulseid"))
        pulsetime = int(m.group("pulsetime"))
        pulsetime = datetime.datetime.utcfromtimestamp(pulsetime)
        return {"pulseid": pulseid, "pulsetime": pulsetime}
    else:
        return {}


def parse_trigger(line):
    pattern = r"CoProcess trigid: (?P<trigid>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        trigid = int(m.group("trigid"))
        return {"trigid": trigid}
    else:
        return {}


def parse_block(line):
    pattern = r"\t\t\tCoProcessing (?P<blockid>\d+) (?P<blocktime>\d*\.?\d*) \|realtime: (?P<realtime>\d*\.?\d*)\| \d*\.?\d* -?\d*\.?\d*"
    m = re.match(pattern, line)
    if m is not None:
        blockid = int(m.group("blockid"))
        blocktime = float(m.group("blocktime"))
        realtime = float(m.group("realtime"))
        blocktime = datetime.datetime.utcfromtimestamp(blocktime)
        realtime = datetime.datetime.utcfromtimestamp(realtime)
        return {"blockid": blockid, "blocktime": blocktime, "realtime": realtime}
    else:
        return {}


def parse_writing(line):
    pattern = r"\[HDF5Writer\]\[Info\] Writing data took (?P<writingtime>\d*\.?\d*) ms"
    m = re.match(pattern, line)
    if m is not None:
        writingtime = round(float(m.group("writingtime")) / 1000, 3)
        return {"writingtime": writingtime}
    else:
        return {}


def parse_coprocessing(line):
    pattern = r"###Coprocessing took (?P<coprocessingtime>\d*\.?\d*) \(seconds\)"
    m = re.match(pattern, line)
    if m is not None:
        coprocessingtime = round(float(m.group("coprocessingtime")), 3)
        return {"coprocessingtime": coprocessingtime}
    else:
        return {}


def parse_timeout(line):
    pattern = "A timeout occurred while waiting for trigger during TSR acquisition"
    if pattern in line:
        return {"timeout": True}
    else:
        return {}


def parse_ready(line):
    pattern = "Starting Acquisition driver 1 build recette2-591-g18b8"
    if pattern in line:
        return {"ready": True}
    else:
        return {}


def parse_serial(line):
    pattern = "DEBUG : serial execution error"
    if pattern in line:
        return {"serial": True}
    else:
        return {}
