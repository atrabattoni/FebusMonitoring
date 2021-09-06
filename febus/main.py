from configparser import ConfigParser
import logging

from .monitor import Monitor


def main():
    print("Welcome to the Febus Monitoring Tool!")
    print("Logging information can be found in the 'log' file.")
    logging.basicConfig(filename='log', format='%(asctime)s: %(message)s')
    config = get_config()
    monitor = Monitor(config)
    monitor.setup()
    monitor.loop()
    monitor.terminate()


def get_config():
    try:
        config = ConfigParser()
        config.read("config")
        logging.info("Config file loaded.")
        return config
    except FileNotFoundError:
        logging.info("Config file not found.")
        exit()
