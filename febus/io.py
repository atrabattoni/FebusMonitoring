import importlib.util
from pathlib import Path


def input_bool(question):
    answer = input(f"{question} [y/n]: ")
    if answer == "y":
        out = True
    elif answer == "n":
        out = False
    else:
        print("Answer not understood. Must be 'y' or 'n'.")
        input_bool(question)
    return out


def input_int(name):
    out = input(f"{name}: ")
    try:
        return int(out)
    except ValueError:
        print("Inputed string could not converted to integer.")
        input_int(name)


def input_float(name):
    out = input(f"{name}: ")
    try:
        return float(out)
    except ValueError:
        print("Inputed string could not converted to float.")
        input_int(name)


def input_path(name):
    path = Path(input(f"{name}: "))
    if path.exists():
        return path
    else:
        print("File not found.")
        input_path(name)


def import_path(path):
    spec = importlib.util.spec_from_file_location(path.name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def input_params():
    return dict(
        fiber_length=input_int("Fiber length [m]"),
        frequency_resolution=input_float("Frequency resolution [Hz]"),
        spatial_resolution=input_int("Pulse width [m]"),
        ampli_power=input_int("Ampli power [dBm]"),
        cutoff_frequency=input_int("Pulse Frequency [Hz]"),
        gauge_length=1,
        sampling_resolution=input_int("Sampling resolution [cm]"),
        pipeline=input_path("Pipeline path"),
    )
