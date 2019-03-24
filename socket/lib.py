import json
import logging
from collections import namedtuple


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

# Source: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}


def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True, style='%'):
        logging.Formatter.__init__(self, msg, style=style)
        self.use_color = use_color


    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


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
    formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] - %(message)s')
    FORMAT = '%(asctime)s - $BOLD%(name)s$RESET [%(levelname)19s] "%(message)s" ($BOLD%(filename)s$RESET:%(lineno)d)'
    # FORMAT = "[{levelname:^8s}]"
    COLOR_FORMAT = formatter_message(FORMAT, use_color=True)
    color_formatter = ColoredFormatter(COLOR_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(color_formatter)

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
