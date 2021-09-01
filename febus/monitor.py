import datetime
import multiprocessing
import os
import pathlib
import time
import threading

from .parser import parse


class Monitor:

    def __init__(self, device, params, data_processor):
        self.device = device
        self.params = params
        self.data_processor = data_processor
        self.currentfile = None
        self.oldfiles = list(pathlib.Path(".").glob("*.h5"))
        self.info = {}
        self.stream = []
        self.isnewfile = False
        self.temporary_disabled = False
        self.is_monitoring = True

        def target():
            for line in self.device.server.stdout:
                self.monitor(line)
                if not self.is_monitoring:
                    break

        self.thread = threading.Thread(target=target)
        self.thread.start()
        print("Monitoring started.")

    def __del__(self):
        self.is_monitoring = False
        self.thread.join()
        print("Monitoring terminated.")

    def monitor(self, line):
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
        if None in self.info.values():
            error = True
        else:
            error = False
        self.log_info(error=error)
        self.dump_info(error=error)
        self.dump_lines(error=error)
        print(".", end="", flush=True)

    def callback_3236(self, blocktime):
        print()
        print("An 3236 error occured.")
        if blocktime > datetime.datetime(3000, 1, 1):
            self.device.disable()
            self.temporary_disabled = True
        else:
            if self.temporary_disabled:
                self.device.enable()
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
