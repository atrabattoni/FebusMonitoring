from configparser import ConfigParser

from .monitor import Monitor


def main():
    print("Welcome to the Febus Monitoring Tool!")
    config = get_config()
    monitor = Monitor(config)
    monitor.setup()
    monitor.loop()
    monitor.terminate()


def get_config():
    try:
        config = ConfigParser()
        config.read("config")
        print("Config file loaded.")
        return config
    except FileNotFoundError:
        print("Config file not found.")
        exit()
