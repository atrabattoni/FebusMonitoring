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

    def __init__(self, gps):
        if not gps in ["yes", "no"]:
            print("Wrong GPS argument. Must be 'yes' or 'no'.")
        self.gps = gps

    def start_server(self):
        cmd = ["stdbuf", "-oL", "-eL", "/opt/febus-a1/bin/run-server.sh"]
        if self.gps == "yes":
            cmd.append("gps")
            print("Enabling GPS.")
        else:
            print("Disabling GPS.")
        self.server = subprocess.Popen(
            cmd,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            text=True,
        )
        self.server.stdout.reconfigure(line_buffering=True, write_through=True)
        atexit.register(self.terminate_server)
        time.sleep(3)
        print("Server started.")

    def terminate_server(self):
        try:
            os.killpg(os.getpgid(self.server.pid), signal.SIGTERM)
            self.server.wait()
            print("Server terminated.")
        except ProcessLookupError:
            print("Server already terminated.")

    @staticmethod
    def start_acquisition(fiber_length, frequency_resolution,
                          spatial_resolution, ampli_power, cutoff_frequency,
                          gauge_length, sampling_resolution, pipeline):
        cmd = [
            "/opt/febus-a1/bin/ClientCli", "-c", "start",
            fiber_length,  # m [int]
            frequency_resolution,  # Hz [float]
            spatial_resolution,  # m [int]
            ampli_power,  # dBm [float]
            cutoff_frequency,  # Hz [int]
            gauge_length,  # m [int]
            sampling_resolution,  # cm [int]
            pipeline,
        ]
        subprocess.call(cmd, env=ENV)
        print("Acquisition started.")

    @staticmethod
    def stop_acquisition():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "stop"]
        subprocess.call(cmd, env=ENV)
        print("Acquisition stopped.")

    @staticmethod
    def get_status():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-status"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        return out.splitlines()[1]

    @staticmethod
    def get_params():
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-params"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        d = {}
        for s in out.splitlines()[1:]:
            key, value = s.split(":")
            key = key.strip()
            value = value.strip()
            d[key] = value
        return d

    @staticmethod
    def enable_writings():
        cmd = ["rm", "-f", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings enabled.")

    @staticmethod
    def disable_writings():
        cmd = ["touch", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings disabled.")
