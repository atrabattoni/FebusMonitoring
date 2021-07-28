import time

from . import parser


class Watcher():

    def __init__(self, info_fname, lines_fname):
        self.info_fname = info_fname
        self.lines_fname = lines_fname
        self.info = {}
        self.lines = []

    def parse(self, line):
        if parser.parse_new_loop(line):
            self.dump_info()
            self.dump_lines()

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

        self.lines.append(line)

    def dump_info(self):
        with open(self.info_fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")
                self.info[key] = None

    def dump_lines(self):
        with open(self.lines_fname, "w") as file:
            file.writelines(self.lines)
        self.lines = []
