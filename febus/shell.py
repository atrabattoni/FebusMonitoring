import time

from .cli import FebusDevice
from .io import import_path, input_bool, input_params, input_path
from .monitor import Monitor


def fsh():
    print("Welcome to Febus shell!")
    try:
        # Input settings
        gps = input_bool("Would you like to use GPS synchronisation?")
        params = input_params()
        if input_bool("Would you like to use a data processor?"):
            path = input_path("Data processor path")
            module = import_path(path)
            data_processor = module.data_processor
        else:
            data_processor = None
        # Start Acquisition
        device = FebusDevice(gps=gps)
        monitor = Monitor(device, params, data_processor)
        device.start_acquisition(**params)
        device.enable_writings()
        print("To stop the acquisition press CTRL+C.")
        device.server.wait()
    except KeyboardInterrupt:
        print()
        if input_bool("Are you sure you want to stop the acquisition?"):
            device.disable_writings()
            time.sleep(1)
            del monitor
            del device
            exit()
        else:
            print("Resuming acquisition...")
