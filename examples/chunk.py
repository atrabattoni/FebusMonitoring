"""
Allows to write smaller files than one hour by enabling and disabling HDF5 writing.
"""

from febus.cli import launch, start, enable
from febus.monitor import chunk

server = launch(gps=False)
enable()
start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
chunk(server, 10)
