import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.enable()
fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")

watcher = fw.Watcher("state", "raw_state")

while True:
    line = server.stdout.readline()
    watcher.parse(line)
