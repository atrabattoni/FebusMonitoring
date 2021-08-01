import atexit
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
        pass

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
    while True:
        print("Hello world!", flush=True)
        time.sleep(1)
