import json
import logging
from collections import namedtuple


def config_logger(app_name):
    # create logger with 'spam_application'
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def as_int(d):
    if "port" in d:
        d["port"] = eval(d["port"])
    return d


def load_host_config(filename):
    config = dict()
    with open(filename, 'r') as f:
        config = json.load(f, object_hook=as_int)
    host_config = namedtuple("HostConfig", config.keys())(*config.values())
    return host_config


if __name__ == '__main__':
    # Get the host configuration
    host_config = load_host_config("host_config.json")
    # host_config = load_host_config(sys.argv[1])

    for prop, value in vars(host_config).iteritems():
        print("{:s}: {:s}".format(prop, value))
