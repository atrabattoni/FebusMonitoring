import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.start(4500, 1, 2, 30, 2000, 1, 40, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
watcher = fw.Watcher()
for line in server.stdout:
    watcher.parse(line)
