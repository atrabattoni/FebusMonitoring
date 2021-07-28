import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
watcher = fw.Watcher(server, "state", "raw_state")
watcher.run()
fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
