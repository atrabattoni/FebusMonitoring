import datetime
import multiprocessing
import os
import pathlib
import threading

from . import parser


class Watcher:

    def __init__(self, device, data_processor):
        self.device = device
        self.data_processor = data_processor
        self.currentfile = None
        self.oldfiles = list(pathlib.Path(".").glob("*.h5"))
        self.info = {}
        self.stream = []
        self.isnewfile = False
        self.temporary_disabled = False

    def start_monitoring(self):
        self.monitoring = True

        def monitoring():
            for line in self.device.server.stdout:
                self.parse(line)
                if not self.monitoring:
                    break

        self.thread = threading.Thread(target=monitoring)
        self.thread.start()
        print("Monitoring Started")

    def terminate_monitoring(self):
        self.monitoring = False
        self.thread.join()
        print("Monitoring Terminated")

    def parse(self, line):
        result = parser.parse(line)
        if isinstance(result, str):
            if result == "newloop":
                if None in self.info.values():
                    error = True
                else:
                    error = False
                self.log_info(error=error)
                self.dump_info(error=error)
                self.dump_lines(error=error)
            elif result == "newloop":
                error = True
            else:
                pass
        if isinstance(result, dict):
            self.info.update(result)
            if "blocktime" in result:
                blocktime = result["blocktime"]
                # Solve 3236 Error
                if blocktime > datetime.datetime(3000, 1, 1):
                    self.device.disable()
                    self.temporary_disabled = True
                else:
                    if self.temporary_disabled:
                        self.device.enable()
                        self.temporary_disabled = False
            if "writingtime" in result:
                self.watch_files()
                self.info["currentfile"] = self.currentfile
                self.info["currentsize"] = self.currentfile.stat().st_size
        self.stream.append(line)

    def watch_files(self):
        files = list(pathlib.Path(".").glob("*.h5"))
        newfiles = [file for file in files if file not in self.oldfiles]
        self.oldfiles.extend(newfiles)
        if len(newfiles) == 1:
            newfile, = newfiles
            self.isnewfile = True

            # Process old file
            if (self.data_processor is not None) and (self.currentfile is not None):
                def data_processor(fname):
                    os.nice(19)
                    self.data_processor(fname)
                process = multiprocessing.Process(
                    target=data_processor, args=(self.currentfile,))
                process.start()

            self.currentfile = newfile

        else:
            self.isnewfile = False

    def log_info(self, error=False):
        fname = str(self.currentfile).replace(".h5", ".log")
        if error:
            fname = fname.replace(".log", "_error.log")
        sep = ","
        with open(fname, "a") as file:
            if self.isnewfile is not None:
                file.write(sep.join(self.info.keys()) + "\n")
            values = [str(value) for value in self.info.values()]
            file.write(sep.join(values) + "\n")

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
            file.writelines(self.stream)
        self.stream = []
