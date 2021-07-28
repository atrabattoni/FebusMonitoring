import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
file_watcher = fw.FileWatcher()
terminal_watcher = fw.TerminalWatcher(
    server, [file_watcher], "state", "raw_state")
while True:
    line = server.stdout.readline()
    terminal_watcher.parse(line)
