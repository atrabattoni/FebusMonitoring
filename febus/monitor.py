import datetime
import importlib.util
import itertools
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path

from .device import FebusDevice
from .parser import parse


class Monitor:
    def __init__(self, config):
        self.config = config
        gps = self.config["server"]["gps"]
        data_processor = config["monitor"]["data_processor"]
        self.device = FebusDevice(gps=gps)
        self.time_monitor = TimeMonitor(self.device)
        self.file_monitor = FileMonitor(data_processor=data_processor)
        self.state = State()
        self.stream = Stream()

    def setup(self):
        self.device.start_server()
        self.wait_ready()
        self.device.start_acquisition(**self.config["acquisition"])
        self.device.enable_writings()

    def loop(self):
        print("To stop the acquisition press CTRL+C.")
        spinner = Spinner()
        try:
            while True:
                line = self.device.get_line()
                if line is not None:
                    info = parse(line)
                    if "newloop" in info:
                        self.callback_newloop()
                        spinner.spin()
                    if "timeout" in info:
                        self.callback_timeout()
                    if "gpstime" in info:
                        self.time_monitor.monitor(info["gpstime"])
                    if "writingtime" in info:
                        out = self.file_monitor.monitor()
                        info.update(out)
                    if "serial" in info:
                        logging.info("Serial execution error.")
                    self.stream.update(line)
                    self.state.update(info)
                else:
                    time.sleep(0.001)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped.")

    def terminate(self):
        self.device.disable_writings()
        self.wait_loop()
        self.device.stop_acquisition()
        self.device.terminate_server()
        self.file_monitor.process_data()
        print("Thanks for using FebusMonitoring!")

    def wait_loop(self):
        frequency_resolution = float(
            self.config["acquisition"]["frequency_resolution"])
        loop_duration = 1 / frequency_resolution
        time.sleep(loop_duration)

    def wait_ready(self):
        is_ready = False
        while is_ready:
            line = self.device.get_line()
            self.stream.update(line)
            if line is not None:
                info = parse(line)
                if "ready" in info:
                    is_ready = True
            else:
                time.sleep(0.001)
        logging.info("Server is ready.")
        time.sleep(1)

    def callback_newloop(self):
        if self.state.is_complete():
            self.state.log(
                str(self.file_monitor.current_file).replace(".h5", ".log"))
            self.state.write()
            self.stream.write()
        else:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.state.write(f"state_{now}")
            self.stream.write(f"stream_{now}")
        self.state.reset()
        self.stream.reset()

    def callback_timeout(self):
        logging.info("A timeout error occured. Relaunching acquisition...")
        self.wait_loop()
        self.device.start_acquisition(**self.config["acquisition"])


class Spinner:
    def __init__(self):
        self.characters = itertools.cycle(['-', '\\', '|', '/'])

    def spin(self):
        sys.stdout.write(next(self.characters))
        sys.stdout.flush()
        sys.stdout.write('\b')


class TimeMonitor:
    def __init__(self, device):
        self.device = device
        self.temporary_disabled = False
        self.wait_for_next_gpstime = False

    def monitor(self, gpstime):
        if gpstime > datetime.datetime(3000, 1, 1):
            if not self.temporary_disabled:
                logging.info("GPS is in 3236 state.")
                self.device.disable_writings()
                self.temporary_disabled = True
                self.wait_for_next_gpstime = True
        else:
            if self.temporary_disabled:
                logging.info("GPS time recovered.")
                self.temporary_disabled = False
            elif self.wait_for_next_gpstime:
                logging.info("Ready to enable writings.")
                self.device.enable_writings()
                self.wait_for_next_gpstime = False


class FileMonitor:
    def __init__(self, data_processor):
        self.current_file = None
        self.previous_files = list(Path(".").glob("*.h5"))
        self.data_processor = self.import_data_processor(data_processor)

    def monitor(self):
        files = list(Path(".").glob("*.h5"))
        new_files = [file for file in files if file not in self.previous_files]
        self.previous_files.extend(new_files)
        if len(new_files) == 0:
            pass
        elif len(new_files) == 1:
            newfile, = new_files
            logging.info(f"New file opened: {newfile}.")
            self.process_data()
            self.current_file = newfile
        else:
            raise RuntimeError("Too many new files.")
        out = {}
        out["currentfile"] = self.current_file
        if self.current_file is not None:
            out["currentsize"] = self.current_file.stat().st_size
        return out

    @staticmethod
    def import_data_processor(path):
        if path == "no":
            return None
        else:
            spec = importlib.util.spec_from_file_location(path, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.data_processor

    def process_data(self):
        if (self.data_processor is not None) and (self.current_file is not None):

            def target(fname):
                os.nice(19)
                self.data_processor(fname)
                logging.info(f"File {self.current_file} processed.")

            process = Process(target=target, args=(self.current_file,))
            process.start()
            logging.info(
                f"Processing {self.current_file} in the background...")


class State:
    def __init__(self):
        self.keys = ["walltime", "pulseid", "pulsetime", "trigid", "blockid",
                     "blocktime", "realtime", "writingtime", "currentfile",
                     "currentsize", "coprocessingtime"]
        self.reset()

    def reset(self):
        self.state = dict.fromkeys(self.keys)

    def update(self, d):
        self.state.update({key: d[key] for key in self.keys if key in d})

    def is_complete(self):
        return (None not in self.state.values())

    def write(self, fname="state"):
        with open(fname, "w") as file:
            for key, item in self.state.items():
                file.write(f"{key}: {item}\n")

    def log(self, fname):
        sep = ","
        with open(fname, "a") as file:
            if file.tell() == 0:
                file.write(sep.join(self.state.keys()) + "\n")
            values = [str(value) for value in self.state.values()]
            file.write(sep.join(values) + "\n")


class Stream:
    def __init__(self):
        self.reset()

    def reset(self):
        self.lines = []

    def update(self, line):
        self.lines.append(line)

    def write(self, fname="stream"):
        with open(fname, "w") as file:
            file.writelines(self.lines)
