"""
Run an acquisition in a robust way. Restarts the acquisition if any problem.
"""

from __future__ import print_function
from febus.monitor import robust
from febus.cli import launch, start, enable
import datetime

import sys
sys.path.append("/home/febus/febus")  # depend on the folder location

params = {
    "fiber_length": 2000,
    "frequency_resolution": 1,
    "spatial_resolution": 1,
    "ampli_power": 24,
    "cutoff_frequency": 1000,
    "gauge_length": 10,
    "sampling_resolution": 80,
    "pipeline_fname": "/home/febus/Pipelines/SR_writer.py",
}

server = launch()
enable()
start(**params)
robust(params)
