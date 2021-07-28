import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.start(4500, 2, 1, 30, 2000, 1, 40, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
file_watcher = fw.FileWatcher()
terminal_watcher = fw.TerminalWatcher(
    server, [file_watcher], "state", "raw_state")
while True:
    line = server.stdout.readline()
    terminal_watcher.parse(line)
