import cmd
import time

from .cli import FebusDevice
from .io import import_path, input_bool, input_params, input_path
from .watcher import Watcher


def fsh():
    FebusShell().cmdloop()


class FebusShell(cmd.Cmd):
    intro = "Type help or ? to list commands."
    prompt = "(febus) "

    def preloop(self):
        # Input settings
        self.gps = input_bool("Would you like to use GPS synchronisation ?")
        self.params = input_params()
        if input_bool("Would you like to use a data processor ?"):
            path = input_path("Data processor path")
            module = import_path
            self.data_processor = module.data_processor
        else:
            self.data_processor = None
        # Start Acquisition
        self.device = FebusDevice(gps=self.gps)
        self.monitor = Watcher(self.device, data_processor=self.data_processor)
        self.monitor.start_monitoring()
        self.device.start_acquisition(**self.params)
        self.device.enable_writings()

    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")

    def do_status(self, arg):
        ""
        print(self.device.get_status())

    def do_params(self, arg):
        ""
        print(self.device.get_params())
        # for key, item in self.device.get_params().items:
        #     print(key, item)

    def do_writings(self, arg):
        ""
        if arg == "enable":
            self.device.enable_writings()
        elif arg == "disable":
            self.device.disable_writings()
        else:
            print("Argument not understood. Must be 'enable' or 'disable'")

    def do_info(self, arg):
        if self.watcher is not None:
            for key, item in self.watcher.info.items():
                print(f"{key}: {item}")
        else:
            print("Watcher not started.")

    def do_exit(self, arg):
        self.device.disable_writings()
        time.sleep(1)
        self.device.stop_acquisition()
        time.sleep(1)
        del self.device
        exit()
