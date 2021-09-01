import sys
import time

from .cli import FebusDevice
from .io import import_path, input_bool, input_config, write_config, read_config
from .monitor import Monitor


def fsh():
    print("Welcome to Febus shell!")
    # Input settings
    if len(sys.argv) <= 1:
        config = input_config()
        write_config(config)
    elif len(sys.argv) == 2:
        config = read_config(sys.argv[1])
    else:
        print("Wrong number of arguments. Should be zero for manual parameter "
              "selection, or one to specify the configuration file.")
        exit()
    # Start Acquisition
    try:
        module = import_path(config["monitor"]["data_processor"])
        data_processor = module.data_processor
        device = FebusDevice(gps=config["server"]["gps"])
        monitor = Monitor(device, config["acquisition"], data_processor)
        device.start_acquisition(**config["acquisition"])
        device.enable_writings()
        print("To stop the acquisition press CTRL+C.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        if input_bool("Are you sure you want to stop the acquisition?") == "yes":
            device.disable_writings()
            time.sleep(1)
            del monitor
            del device
            exit()
        else:
            print("Resuming acquisition...")
