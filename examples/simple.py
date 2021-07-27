from febus.cli import launch, start, enable
from febus.monitor import chunk

server = launch(gps=False)
enable()
start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")

while True:
    print(server.stdout.readline(), end="")
