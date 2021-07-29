import datetime
import pathlib
import threading

import daspy.io

from . import cli, parser


class Watcher():

    def __init__(self):
        self.currentfile = None
        self.directory = pathlib.Path(".")
        self.files = list(self.directory.glob("*.h5"))
        self.info = {}
        self.lines = []
        self.newfile = None
        self.temporary_disabled = False

    def parse(self, line):
        if parser.parse_newloop(line):
            if None in self.info.values():
                error = True
            else:
                error = False
            self.log_info(error=error)
            self.dump_info(error=error)
            self.dump_lines(error=error)

        pulseid, pulsetime = parser.parse_pulse(line)
        if (pulsetime is not None) and (pulseid is not None):
            self.info["pulseid"] = pulseid
            self.info["pulsetime"] = pulsetime

        walltime = parser.parse_walltime(line)
        if walltime is not None:
            self.info["walltime"] = walltime

        trigid = parser.parse_trigger(line)
        if trigid is not None:
            self.info["trigid"] = trigid

        blockid, blocktime, realtime = parser.parse_block(line)
        if (blockid is not None) and (blocktime is not None) and (realtime is not None):
            self.info["blockid"] = blockid
            self.info["blocktime"] = blocktime
            self.info["realtime"] = realtime

            # Solve 3236 Error
            if blocktime > datetime.datetime(3000, 1, 1):
                cli.disable()
                self.temporary_disabled = True
            else:
                if self.temporary_disabled:
                    cli.enable()
                    self.temporary_disabled = False

        writingtime = parser.parse_writing(line)
        if writingtime is not None:
            self.info["writingtime"] = writingtime
            self.watch_files()
            self.info["currentfile"] = self.currentfile

        coprocessingtime = parser.parse_coprocessing(line)
        if coprocessingtime is not None:
            self.info["coprocessingtime"] = coprocessingtime

        self.lines.append(line)

    def dump_info(self, error=False):
        fname = "info"
        if error:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            fname += f"_error_{now}"
        with open(fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")
                self.info[key] = None

    def dump_lines(self, error=False):
        fname = "stream"
        if error:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            fname += f"_error_{now}"
        with open(fname, "w") as file:
            file.writelines(self.lines)
        self.lines = []

    def watch_files(self):
        files = list(self.directory.glob("*.h5"))
        newfiles = [file for file in files if file not in self.files]
        self.files.extend(newfiles)
        if len(newfiles) == 1:
            self.newfile, = newfiles

            # Process old file
            if self.currentfile is not None:
                th = threading.Thread(target=process, args=(self.currentfile,))
                th.start()

            self.currentfile = self.newfile

        else:
            self.newfile = None

    def log_info(self, error=False):
        fname = str(self.currentfile).replace(".h5", ".log")
        if error:
            fname = fname.replace(".log", "_error.log")
        sep = ","
        with open(fname, "a") as file:
            if self.newfile is not None:
                file.write(sep.join(self.info.keys()) + "\n")
            values = [str(value) for value in self.info.values()]
            file.write(sep.join(values) + "\n")


def process(fname):
    xarr = daspy.io.read(fname)
    xarr = daspy.io.trim(fname)
    fname = fname.replace(".h5", ".nc")
    xarr.to_netcdf(fname)
