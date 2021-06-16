"""
Allows to write smaller files than one hour by enabling and disabling HDF5 writing.
"""

from __future__ import print_function

import sys
sys.path.append("/home/febus/febus")  # depend on the folder location

import datetime
from febus.cli import launch, start, enable
from febus.monitor import chunk

server = launch()
enable()
start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
chunk(server, 10)
