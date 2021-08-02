import atexit
import datetime
import pathlib
import signal
import subprocess
import sys
import time

# Communication File
STOP_ACQUISITION_PATH = ".stop_acquisition"

# Set path to enable/disable hdf5 writing
STOP_WRITINGS_PATH = ".hdf5_stop_writings"

def dummy():
    pass

class DummyDevice:

    def __init__(self):
        self.stop_acquisition()
        self.disable_writings()

    def start_server(self, gps=False):
        # def preexec_fn():
            # signal.signal(signal.SIGINT, signal.SIG_IGN)
        cmd = [sys.executable, __file__]
        self.server = subprocess.Popen(
            cmd,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # preexec_fn=preexec_fn,
            text=True,
        )
        self.server.stdout.reconfigure(line_buffering=True, write_through=True)
        self.server.gps = gps
        atexit.register(self.terminate_server)
        time.sleep(1)
        print("Server Started")

    def terminate_server(self):
        self.server.terminate()
        print("Server Terminated")

    @staticmethod
    def start_acquisition(*args, **kwargs):
        cmd = ["rm", "-f", STOP_ACQUISITION_PATH]
        subprocess.call(cmd)

    @staticmethod
    def stop_acquisition():
        cmd = ["touch", STOP_ACQUISITION_PATH]
        subprocess.call(cmd)

    @staticmethod
    def get_status():
        pass

    @staticmethod
    def get_params():
        pass

    @staticmethod
    def enable_writings():
        cmd = ["rm", "-f", STOP_WRITINGS_PATH]
        subprocess.call(cmd)

    @staticmethod
    def disable_writings():
        cmd = ["touch", STOP_WRITINGS_PATH]
        subprocess.call(cmd)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print("Dummy device started.")
    utcdatetime = datetime.datetime.utcnow()
    walltime = 1.0
    pulseid = 0
    pulsetime = utcdatetime
    trigid = 0
    blockid = 0
    blocktime = utcdatetime
    realtime = utcdatetime
    writingtime = 2.0
    coprocessingtime = 0.1

    while True:
        if not pathlib.Path(STOP_ACQUISITION_PATH).is_file():
            print("New loop", flush=True)
            print("[SERVER] cuda block wall clock {walltime}")
            print("CoProcess ref pulseID: {pulseid} timestamp:{pulsetime}")
            print("CoProcess trigid: {trigid}")
            print("CoProcessing {blockid} {blocktime} |realtime: {realtime}")
            if not pathlib.Path(STOP_WRITINGS_PATH).is_file():
                print("[HDF5Writer][Info] Writing data took {writingtime} ms")
            print("Coprocessing took {coprocessingtime} (seconds)")
        time.sleep(1)
