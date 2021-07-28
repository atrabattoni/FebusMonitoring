import time

from . import parser


class RawStateUpdater():

    def __init__(self, fname):
        self.fname = fname
        self.lines = []

    def parse(self, line):
        if parser.parse_new_loop(line):
            self.dump()
        self.lines += line

    def dump(self):
        with open(self.fname, "w") as file:
            file.writelines(self.lines)
        self.lines = []


class StateUpdater():

    def __init__(self, fname):
        self.fname = fname
        self.info = {}

    def parse(self, line):
        if parser.parse_new_loop(line):
            self.dump()

        gpstime, pulseid = parser.parse_gpstime_pulseid(line)
        if (gpstime is not None) and (pulseid is not None):
            self.info["gpstime"] = gpstime
            self.info["pulseid"] = pulseid

        walltime = parser.parse_walltime(line)
        if walltime is not None:
            self.info["walltime"] = walltime

        trigid = parser.parse_trigid(line)
        if trigid is not None:
            self.info["trigid"] = trigid

        utcdatetime, blockid = parser.parse_utcdatetime_blockid(line)
        if (utcdatetime is not None) and (blockid is not None):
            self.info["utcdatetime"] = utcdatetime
            self.info["blockid"] = blockid

        writetime = parser.parse_writetime(line)
        if writetime is not None:
            self.info["writetime"] = writetime

        coprocessingtime = parser.parse_coprocessingtime(line)
        if coprocessingtime is not None:
            self.info["coprocessingtime"] = coprocessingtime

    def dump(self):
        with open(self.fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")
