import datetime
import multiprocessing
import os
import pathlib
import time

from .cli import FebusDevice
from .io import import_path
from .parser import parse


class Monitor:

    def __init__(self, config):
        self.gps = config["server"]["gps"]
        self.params = config["acquisition"]
        module = import_path(config["monitor"]["data_processor"])
        self.data_processor = module.data_processor
        self.loop_duration = 1 / float(self.params["frequency_resolution"])
        self.device = FebusDevice(gps=self.gps)
        self.currentfile = None
        self.oldfiles = list(pathlib.Path(".").glob("*.h5"))
        self.info = {}
        self.stream = []
        self.isnewfile = False
        self.temporary_disabled = False

        self.device.start_acquisition(**self.params)
        self.device.enable_writings()
        print("To stop the acquisition press CTRL+C.")
        try:
            for line in self.self.device.server.stdout:
                self.callback(line)
        except KeyboardInterrupt:
            self.device.disable_writings()
            time.sleep(self.loop_duration)
            self.device.stop_acquisition()
            exit()

    def callback(self, line):
        self.stream.append(line)
        result = parse(line)
        if isinstance(result, str):
            if result == "newloop":
                self.callback_newloop()
            elif result == "timeout":
                self.callback_timeout()
            else:
                print(result)
                print(line)
        if isinstance(result, dict):
            self.info.update(result)
            if "blocktime" in result:
                blocktime = result["blocktime"]
                self.callback_3236(blocktime)
            if "writingtime" in result:
                self.callback_files()

    def callback_newloop(self):
        print(".", end="", flush=True)
        if None in self.info.values():
            error = True
        else:
            error = False
        self.log_info(error=error)
        self.dump_info(error=error)
        self.dump_lines(error=error)

    def callback_3236(self, blocktime):
        if blocktime > datetime.datetime(3000, 1, 1):
            print()
            print("An 3236 error occured.")
            self.device.disable_writings()
            self.temporary_disabled = True
        else:
            if self.temporary_disabled:
                print()
                self.device.enable_writings()
                self.temporary_disabled = False

    def callback_timeout(self):
        print()
        print("A timeout error occured. Relaunching acquisition...")
        time.sleep(1)
        self.device.start_acquisition(**self.params)

    def callback_files(self):
        files = list(pathlib.Path(".").glob("*.h5"))
        newfiles = [file for file in files if file not in self.oldfiles]
        self.oldfiles.extend(newfiles)
        if len(newfiles) == 0:
            self.isnewfile = False
        elif len(newfiles) == 1:
            print()
            newfile, = newfiles
            self.isnewfile = True
            print("New file.")
            self.process_data()
            self.currentfile = newfile
        else:
            print()
            raise RuntimeError("Too many new files.")
        self.info["currentfile"] = self.currentfile
        if self.currentfile is not None:
            self.info["currentsize"] = self.currentfile.stat().st_size

    def process_data(self):
        if (self.data_processor is not None) and (self.currentfile is not None):
            print("Processing file in the background...")

            def target(fname):
                os.nice(19)
                self.data_processor(fname)
                print("File processed.")
            process = multiprocessing.Process(
                target=target, args=(self.currentfile,))
            process.start()

    def log_info(self, error=False):
        fname = str(self.currentfile).replace(".h5", ".log")
        if error:
            fname = fname.replace(".log", "_error.log")
        sep = ","
        with open(fname, "a") as file:
            if self.isnewfile:
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
