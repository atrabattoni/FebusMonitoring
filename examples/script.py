import time
import febus.watcher as fp

# to change by the user
fname = "/home/trabattoni/Desktop/das/data/log/SR_2021-03-30.log"

raw_state_updater = fp.RawStateUpdater("raw_state")
state_updater = fp.StateUpdater("state")
line = True
with open(fname, "r") as server:  # the file simulate the server
    while line:
        line = server.readline()
        raw_state_updater.parse(line)
        state_updater.parse(line)
        time.sleep(0.001)
