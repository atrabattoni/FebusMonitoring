from __future__ import print_function

import datetime
import os
import re
import subprocess
import time

from signal import signal, SIGINT

# Set environment for ClientCli
KEY = "LD_LIBRARY_PATH"
VALUE = """
:/usr/lib64/openmpi/lib/paraview/site-packages/vtk
:/usr/lib64/openmpi/lib/paraview
:/opt/febus-a1/lib:/opt/febus-a1/lib/paraview
"""
ENV = os.environ.copy()
ENV[KEY] = ENV[KEY] + VALUE


def launch():
    """Launch a Catalyst Server with GPS that can be terminated with CTRL+C"""
    server = subprocess.Popen(
        ["/opt/febus-a1/bin/run-server.sh", "gps"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(1)
    print("\nServer Launched")

    def handler(signal_received, frame):
        server.terminate()
        print("\nServer Terminated")
        exit(0)

    signal(SIGINT, handler)
    return server




def start(fiber_length, frequency_resolution, spatial_resolution,
          ampli_power,cutoff_frequency, gauge_length,
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


def parse_error(line):
    """Search for errors"""
    s = re.search(r"error", line, re.IGNORECASE)
    if s is not None:
        return True


def parse_utcdatetime_block(line):
    """Get the UTC datetime of each block"""
    pattern = r"\[CATALYST\] Calling pipeline on block (?P<timestamp>\d+)\.\d+ (?P<block>\d+)"
    m = re.match(pattern, line)
    if m is not None:
        timestamp = float(m.group("timestamp"))
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)
        block = int(m.group("block"))
        return utcdatetime, block
    else:
        return None, None


def parse_gpstime(line):
    """Get the GPS time information"""
    pattern = r"GENEPULSE Sending TimeStamp"
    m = re.match(pattern, line)
    return m


def monitor(server):
    while True:
        line = server.stdout.readline()
        utcdatetime, block = parse_utcdatetime_block(line)
        if utcdatetime and block:
            print(utcdatetime, block)
        gpstime = parse_gpstime(line)
        if gpstime:
            print(line)


if __name__ == "__main__":
    server = launch()
    start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
    monitor(server)



