import json
from collections import namedtuple


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
