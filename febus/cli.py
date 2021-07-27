"""
Python wrappers to Febus CLI tools. Lauching the server withing python allows
to get the output of the terminal for further parsing. 
"""

import os
import subprocess
import time
from signal import SIGINT, signal, getsignal

# Set environment for ClientCli
KEY = "LD_LIBRARY_PATH"
VALUE = """
:/usr/lib64/openmpi/lib/paraview/site-packages/vtk
:/usr/lib64/openmpi/lib/paraview
:/opt/febus-a1/lib:/opt/febus-a1/lib/paraview
"""
ENV = os.environ.copy()
ENV[KEY] = ENV[KEY] + VALUE

# Set path to enable/disable hdf5 writing
STOP_WRITINGS_PATH = "/home/febus/.hdf5_stop_writings"


def launch(gps=True):
    """Launch a Catalyst Server that can be terminated with CTRL+C"""
    cmd = ["stdbuf", "-oL", "-eL", "/opt/febus-a1/bin/run-server.sh"]
    if gps:
        cmd.append("gps")
    server = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(1)
    print("Server Launched")

    original_handler = getsignal(SIGINT)

    def handler(signal_received, frame):
        server.terminate()
        print("\nServer Terminated")
        signal(SIGINT, original_handler)
        raise KeyboardInterrupt

    signal(SIGINT, handler)
    return server


def start(fiber_length, frequency_resolution, spatial_resolution,
          ampli_power, cutoff_frequency, gauge_length,
          sampling_resolution, pipeline_fname):
    """Start Catalyst Server acquisition"""
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


def stop():
    """Stop Catalyst Server acquisition"""
    subprocess.call(
        [
            "/opt/febus-a1/bin/ClientCli",
            "-c",
            "stop",
        ],
        env=ENV,
    )


def get_status():
    """Get Catalyst Server status"""
    out = subprocess.check_output(
        [
            "/opt/febus-a1/bin/ClientCli",
            "-c",
            "get-status",
        ],
        env=ENV,
    )
    return out.splitlines()[1]


def get_params():
    """Get Catalyst Server status"""
    out = subprocess.check_output(
        [
            "/opt/febus-a1/bin/ClientCli",
            "-c",
            "get-params",
        ],
        env=ENV
    )
    return out.splitlines()[1:]


def enable():
    """Enable HDF5 writing"""
    try:
        os.remove(STOP_WRITINGS_PATH)
    except OSError:
        pass


def disable():
    """Disable HDF5 writing"""
    open(STOP_WRITINGS_PATH, "a").close()
