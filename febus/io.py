import importlib.util
from configparser import ConfigParser
from pathlib import Path


def input_bool(question):
    out = input(f"{question} [yes/no]: ")
    if out in ("yes", "no"):
        return out
    else:
        print("Answer not understood. Must be 'yes' or 'no'.")
        return input_bool(question)


def input_int(name):
    out = input(f"{name}: ")
    try:
        return str(int(out))
    except ValueError:
        print("Inputed string could not converted to integer.")
        return input_int(name)


def input_float(name):
    out = input(f"{name}: ")
    try:
        return str(float(out))
    except ValueError:
        print("Inputed string could not converted to float.")
        return input_float(name)


def input_path(name):
    path = Path(input(f"{name}: "))
    if path.exists():
        return path.name
    else:
        print("File not found.")
        return input_path(name)


def import_path(path):
    spec = importlib.util.spec_from_file_location(path, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def input_params():
    return dict(
        fiber_length=input_int("Fiber length [m]"),
        frequency_resolution=input_float("Frequency resolution [Hz]"),
        spatial_resolution=input_int("Pulse width [m]"),
        ampli_power=input_float("Ampli power [dBm]"),
        cutoff_frequency=input_int("Pulse Frequency [Hz]"),
        gauge_length=1,
        sampling_resolution=input_int("Sampling resolution [cm]"),
        pipeline=input_path("Pipeline path"),
    )


def input_config():
    config = ConfigParser()
    config["server"] = {}
    config["server"]["gps"] = input_bool(
        "Would you like to use GPS synchronisation?")
    config["acquisition"] = input_params()
    config["monitor"] = {}
    if input_bool("Would you like to use a data processor?") == "yes":
        config["monitor"]["data_processor"] = input_path("Data processor path")
    else:
        config["monitor"]["data_processor"] = "no"
    return config


def write_config(config):
    with open("params.cfg", "w") as configfile:
        config.write(configfile)
    print("Config saved to 'params.cfg'.")


def read_config(path):
    if Path(path).exists():
        config = ConfigParser()
        config.read(path)
        return config
    else:
        print("Config file not found.")
        exit()
