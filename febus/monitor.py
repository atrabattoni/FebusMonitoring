import importlib.util
import itertools
import logging
import os
import sys
from datetime import datetime
from multiprocessing import Process
from pathlib import Path
from queue import Empty
from time import sleep, time

from .device import FebusDevice
from .parser import parse


class Monitor:
    def __init__(self, config):
        self.config = config
        gps = self.config["server"]["gps"]
        data_processor = config["monitor"]["data_processor"]
        self.loop_duration = 1 / float(
            self.config["acquisition"]["frequency_resolution"])
        self.device = FebusDevice(gps=gps)
        self.timeout_monitor = TimeoutMonitor(10 * self.loop_duration)
        self.blocktime_monitor = BlockTimeMonitor()
        self.file_monitor = FileMonitor(data_processor=data_processor)
        self.state = State()
        self.stream = Stream()

    def setup(self):
        self.secure_start_server()
        self.secure_start_acquisition()
        self.device.enable_writings()

    def loop(self):
        print("To stop the acquisition press CTRL+C.")
        spinner = Spinner()
        try:
            while True:
                try:
                    line = self.device.get_line()
                except Empty:
                    sleep(0.001)
                else:
                    info = parse(line)
                    if "newloop" in info:
                        spinner.spin()
                        self.timeout_monitor.update()
                        self.callback_newloop()
                    if "timeout" in info:
                        self.secure_restart_acquisition()
                    if "blocktime" in info:
                        self.blocktime_monitor.monitor(info["blocktime"])
                    if "writingtime" in info:
                        out = self.file_monitor.monitor()
                        info.update(out)
                    if "serial" in info:
                        logging.info("Serial execution error.")
                    self.stream.update(line)
                    self.state.update(info)
                finally:
                    if self.timeout_monitor.is_deep_timeout:
                        self.secure_restart_all()
                    if self.timeout_monitor.is_timeout:
                        self.secure_restart_acquisition()
        except KeyboardInterrupt:
            logging.info("Monitoring stopped.")

    def terminate(self):
        self.device.disable_writings()
        self.wait_loop_duration()
        self.device.stop_acquisition()
        self.device.terminate_server()
        self.file_monitor.process_data()

    def wait_loop_duration(self):
        sleep(self.loop_duration)

    def wait_for(self, key, timeout):
        start_time = time()
        is_ready = False
        while (not is_ready):
            try:
                line = self.device.get_line()
            except Empty:
                sleep(0.001)
            else:
                self.stream.update(line)
                if line is not None:
                    info = parse(line)
                    if key in info:
                        is_ready = True
            finally:
                elapsed_time = time() - start_time()
                if elapsed_time > timeout:
                    raise TimeoutError

    def secure_start_server(self, timeout=10, trials=3):
        if trials == 0:
            logging.info("Could not start server.")
            raise TimeoutError
        else:
            self.device.start_server()
            logging.info("Waiting for server...")
            try:
                self.wait_for("ready", timeout)
            except TimeoutError:
                logging.info("Server did not start. Relaunching.")
                self.device.terminate_server()
                self.secure_start_server(timeout=timeout, trials=trials-1)
            else:
                logging.info("Server is ready.")

    def secure_start_acquisition(self, timeout=60, trials=3):
        if trials == 0:
            logging.info("Could not start acquisition.")
            raise TimeoutError
        else:
            self.device.start_acquisition(**self.config["acquisition"])
            logging.info("Waiting for acquisition...")
            try:
                self.wait_for("newloop", timeout)
            except TimeoutError:
                logging.info("Acquisition did not start.")
                self.device.stop_acquisition(**self.config["acquisition"])
                self.secure_start_server(timeout=timeout, trials=trials-1)
            else:
                logging.info("Acquisition is started.")

    def secure_restart_all(self):
        self.terminate()
        self.wait_loop_duration()
        self.setup()

    def secure_restart_acquisition(self):
        logging.info("A timeout error occured. Relaunching acquisition...")
        self.device.stop_acquisition()
        self.wait_loop_duration()
        self.secure_start_acquisition()

    def callback_newloop(self):
        if self.state.is_complete():
            self.state.log(
                str(self.file_monitor.current_file).replace(".h5", ".log"))
            self.state.write()
            self.stream.write()
        else:
            now = datetime.now()
            self.state.write(f"state_{now}".replace(" ", "T"))
            self.stream.write(f"stream_{now}".replace(" ", "T"))
        self.state.reset()
        self.stream.reset()

    def callback_deep_timeout(self):
        logging.info("A deep timeout error occured. Relaunching server...")
        self.terminate()
        self.wait_loop_duration()
        self.setup()


class Spinner:
    def __init__(self):
        self.characters = itertools.cycle(['-', '\\', '|', '/'])

    def spin(self):
        sys.stdout.write(next(self.characters))
        sys.stdout.flush()
        sys.stdout.write('\b')


class TimeoutMonitor:
    def __init__(self, timeout=10, deep_timeout=60):
        self.timeout = timeout
        self.deep_timeout = deep_timeout
        self.last_update = None

    def update(self):
        self.last_update = time()

    @property
    def elapsed(self):
        if self.last_update is not None:
            return time() - self.last_update
        else:
            return 0

    @property
    def is_timeout(self):
        return self.elapsed > self.timeout

    @property
    def is_deep_timeout(self):
        return self.elapsed > self.deep_timeout


class BlockTimeMonitor:
    def __init__(self):
        self.temporary_disabled = False

    def monitor(self, blocktime):
        if blocktime > datetime(3000, 1, 1):
            if not self.temporary_disabled:
                logging.info("GPS is in 3236 state.")
                self.device.disable_writings()
                self.temporary_disabled = True
        else:
            if self.temporary_disabled:
                logging.info("GPS time recovered.")
                self.device.enable_writings()
                self.temporary_disabled = False


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
