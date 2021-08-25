import atexit
import os
import signal
import subprocess
import time

# Set environment for ClientCli
KEY = "LD_LIBRARY_PATH"
VALUES = [
    "/usr/lib64/openmpi/lib/paraview/site-packages/vtk",
    "/usr/lib64/openmpi/lib/paraview",
    "/opt/febus-a1/lib",
    "/opt/febus-a1/lib/paraview",
]
ENV = os.environ.copy()
if KEY in ENV:
    VALUES = ENV[KEY].split(":") + VALUES
    VALUES = [value for value in VALUES if value]
ENV[KEY] = ":".join(VALUES)

# Set path to enable/disable hdf5 writing
STOP_WRITINGS_PATH = "/home/febus/.hdf5_stop_writings"


class FebusDevice:

    def __init__(self):
        self.server = None

    def start_server(self, gps=False):
        cmd = ["stdbuf", "-oL", "-eL", "/opt/febus-a1/bin/run-server.sh"]
        if gps:
            cmd.append("gps")
        self.server = subprocess.Popen(
            cmd,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            preexec_fn=os.setsid,
        )
        self.server.stdout.reconfigure(line_buffering=True, write_through=True)
        self.server.gps = gps
        atexit.register(self.terminate_server)
        time.sleep(1)
        print(f"Server Started {'with GPS' if gps else ''}")

    def terminate_server(self):
        # self.server.terminate()
        os.killpg(os.getpgid(self.server.pid), signal.SIGTERM)
        print("Server Terminated")

    @staticmethod
    def start_acquisition(fiber_length, frequency_resolution, spatial_resolution,
                          ampli_power, cutoff_frequency, gauge_length,
                          sampling_resolution, pipeline_fname):
        subprocess.call(
            [
                "/opt/febus-a1/bin/ClientCli",
                "-c",
                "start",
                "{:d}".format(fiber_length),  # m
                "{:.1f}".format(frequency_resolution),  # Hz
                "{:d}".format(spatial_resolution),  # m
                "{:.1f}".format(ampli_power),  # dBm
                "{:d}".format(cutoff_frequency),  # Hz
                "{:d}".format(gauge_length),  # m
                "{:d}".format(sampling_resolution),  # cm
                pipeline_fname,
            ],
            env=ENV,
        )
        print("Acquisition Started")

    @staticmethod
    def stop_acquisition():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "stop"]
        subprocess.call(cmd, env=ENV)
        print("Acquisition Stopped")

    @staticmethod
    def get_status():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-status"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        return out.splitlines()[1]

    @staticmethod
    def get_params():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-params"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        return out.splitlines()[1:]

    @staticmethod
    def enable_writings():
        cmd = ["rm", "-f", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings Enabled")

    @staticmethod
    def disable_writings():
        cmd = ["touch", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings Disabled")
