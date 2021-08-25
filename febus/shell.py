import cmd
import importlib.util
import pathlib

from .cli import FebusDevice
from .watcher import Watcher


class FebusShell(cmd.Cmd):
    intro = "Welcome to the febus shell. Type help or ? to list commands.\n"
    prompt = "(febus) "

    def __init__(self, *args, **kwargs):
        self.device = FebusDevice()
        self.watcher = None
        super().__init__(*args, **kwargs)

    def do_server(self, arg):
        ""
        if arg == "start":
            self.device.start_server(gps=False)
        elif arg == "start gps":
            self.device.start_server(gps=True)
        elif arg == "stop":
            self.device.terminate_server()
        else:
            print("Argument not understood. Must be 'start', 'start gps' or 'stop'")

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

    def do_writings(self, arg):
        ""
        if arg == "start":
            self.device.enable_writings()
            print("Writings")
        elif arg == "stop":
            self.device.disable_writings()
            print("Enabling writings")
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


if __name__ == '__main__':
    FebusShell().cmdloop()