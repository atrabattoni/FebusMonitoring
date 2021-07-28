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
            self.info = {}
            self.dump_lines()
            self.lines += line

        self.info["gpstime"], self.info["pulseid"] = (
            parser.parse_gpstime_pulseid(line))
        self.info["walltime"] = parser.parse_walltime(line)
        self.info["trigid"] = parser.parse_trigid(line)
        self.info["utcdatetime"], self.info["blockid"] = (
            parser.parse_utcdatetime_blockid(line))
        self.info["writetime"] = parser.parse_writetime(line)
        self.info["coprocessingtime"] = parser.parse_coprocessingtime(line)

    def dump_info(self):
        with open(self.info_fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")

    def dump_lines(self):
        with open(self.lines_fname, "w") as file:
            file.writelines(self.lines)
        self.lines = []
