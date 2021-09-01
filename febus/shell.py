import sys

from .io import get_config
from .monitor import Monitor


def fsh():
    print("Welcome to the Febus Monitoring Tool!")
    config = get_config(sys.argv)
    Monitor(config)
