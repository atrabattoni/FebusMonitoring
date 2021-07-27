import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.enable()
fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")

raw_state_updater = fw.RawStateUpdater("raw_state")
state_updater = fw.StateUpdater("state")

line = True
while line:
    line = server.stdout.readline().decode()
    raw_state_updater.parse(line)
    state_updater.parse(line)
