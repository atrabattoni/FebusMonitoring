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
        self.gps = gps
        self.params = None
        cmd = ["stdbuf", "-oL", "-eL", "/opt/febus-a1/bin/run-server.sh"]
        if self.gps:
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
        atexit.register(self.__del__)
        time.sleep(1)
        print(f"Server Started {'with GPS' if self.gps else 'without GPS'}")

    def __del__(self):
        try:
            os.killpg(os.getpgid(self.server.pid), signal.SIGTERM)
            self.server.wait()
            print("Server Terminated")
        except ProcessLookupError:
            print("Server Already Terminated")

    def start_acquisition(self, fiber_length, frequency_resolution,
                          spatial_resolution, ampli_power, cutoff_frequency,
                          gauge_length, sampling_resolution, pipeline_fname):

        self.params = dict(
            fiber_length=fiber_length,
            frequency_resolution=frequency_resolution,
            spatial_resolution=spatial_resolution,
            ampli_power=ampli_power,
            cutoff_frequency=cutoff_frequency,
            gauge_length=gauge_length,
            sampling_resolution=sampling_resolution,
            pipeline_fname=pipeline_fname,
        )
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

    def stop_acquisition(self):
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "stop"]
        subprocess.call(cmd, env=ENV)
        print("Acquisition Stopped")

    def get_status(self):
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-status"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        return out.splitlines()[1]

    def get_params(self):
        cmd = ["/opt/febus-a1/bin/ClientCli", "-c", "get-params"]
        out = subprocess.check_output(cmd, env=ENV, text=True)
        return out.splitlines()[1:]

    def enable_writings(self):
        cmd = ["rm", "-f", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings Enabled")

    def disable_writings(self):
        cmd = ["touch", STOP_WRITINGS_PATH]
        subprocess.call(cmd)
        print("Writings Disabled")
