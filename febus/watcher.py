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

        wall_time = parser.parse_wall_time(line)
        if wall_time is not None:
            self.info["wall_time"] = wall_time

        trigid = parser.parse_trigid(line)
        if trigid is not None:
            self.info["trigid"] = trigid

        utcdatetime, blockid = parser.parse_utcdatetime_blockid(line)
        if (utcdatetime is not None) and (blockid is not None):
            self.info["utcdatetime"] = utcdatetime
            self.info["blockid"] = blockid

        write_time = parser.parse_write_time(line)
        if write_time is not None:
            self.info["write_time"] = write_time

        coprocessing_time = parser.parse_coprocessing_time(line)
        if coprocessing_time is not None:
            self.info["coprocessing_time"] = coprocessing_time

    def dump(self):
        with open(self.fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")
