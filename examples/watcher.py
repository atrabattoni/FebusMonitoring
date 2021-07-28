import sys

import febus.cli as fc
import febus.watcher as fw

fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
file_watcher = fw.FileWatcher()
terminal_watcher = fw.TerminalWatcher([file_watcher], "state", "raw_state")
for line in sys.stdin:
    terminal_watcher.parse(line)
