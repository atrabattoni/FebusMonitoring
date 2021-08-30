import cmd
import importlib.util
import pathlib

from .cli import FebusDevice
from .watcher import Watcher


class FebusShell(cmd.Cmd):
    intro = "Type help or ? to list commands."
    prompt = "(febus) "

    def preloop(self):

        print("Welcome to the febus shell.")

        def ask_gps():
            gps = input("Would you like to use GPS synchronisation ? [y/n]: ")
            if gps == "y":
                gps = True
            elif gps == "n":
                gps = False
            else:
                print("Argument not understood. Must be 'y' or 'n'.")
                ask_gps()
            return gps

        self.device = FebusDevice(gps=ask_gps())
        self.watcher = None
        self.preloop = super().preloop

    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")

    def do_acquisition(self, arg):
        ""
        if arg == "start":
            kwargs = {
                "fiber_length": int(input("Fiber length [m]: ")),
                "frequency_resolution": float(input("Frequency resolution [Hz]: ")),
                "spatial_resolution": int(input("Pulse width [m]: ")),
                "ampli_power": int(input("Ampli power [dBm]: ")),
                "cutoff_frequency": int(input("Pulse Frequency [Hz]: ")),
                "gauge_length": 1,
                "sampling_resolution": int(input("Sampling resolution [cm]: ")),
                "pipeline_fname": input("Pipeline path: "),
            }
            self.device.start_acquisition(**kwargs)
        elif arg == "stop":
            self.device.stop_acquisition()
        else:
            print("Argument not understood. Must be 'start' or 'stop'")

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
        if arg == "start":
            self.device.enable_writings()
        elif arg == "stop":
            self.device.disable_writings()
        else:
            print("Argument not understood. Must be 'start' or 'stop'")

    def do_watcher(self, arg):
        ""
        if arg == "start":
            path = input("Data_processor_path :")
            if path:
                path = pathlib.Path(path)
                spec = importlib.util.spec_from_file_location(path.name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                data_processor = module.data_processor
            else:
                data_processor = None
            self.watcher = Watcher(self.device, data_processor=data_processor)
            self.watcher.start_monitoring()
        elif arg == "stop":
            self.watcher.terminate_monitoring()
            self.watcher = None
        else:
            print("Argument not understood. Must be 'start' or 'stop'")

    def do_info(self, arg):
        if self.watcher is not None:
            for key, item in self.watcher.info.items():
                print(f"{key}: {item}")
        else:
            print("Watcher not started.")

    def do_exit(self, arg):
        exit()


def fsh():
    FebusShell().cmdloop()
