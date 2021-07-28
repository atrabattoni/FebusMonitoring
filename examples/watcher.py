import febus.cli as fc
import febus.watcher as fw

server = fc.launch(gps=False)
fc.start(2000, 1, 1, 24, 1000, 10, 80, "/home/febus/Pipelines/SR_writer.py")
fc.enable()
terminal_watcher = fw.TerminalWatcher(server, "state", "raw_state")
file_watcher = fw.TerminalWatcher(server, "state", "raw_state")
while True:
    line = server.stdout.readline()
    terminal_watcher.parse(line)
    file_watcher.watch()
    if file_watcher.newfile is not None:
        print(file_watcher.newfile)
