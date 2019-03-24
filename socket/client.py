import socket
import argparse
from lib import load_host_config


def config_argparser(ap):
    ap.add_argument(
        "--host-config",
        default="config/host_config.json",
        required=False,
        help="The parth to host configuration."
    )


if __name__ == '__main__':
    # Get user arguments
    parser = argparse.ArgumentParser()
    config_argparser(parser)
    args = parser.parse_args()

    # Load configurations
    host_config = load_host_config(args.host_config)

    # Setup socket
    addr = (host_config.hostname, host_config.port)
    s = socket.socket()
    s.connect(addr)

    print("Connected to server.")

    data = input("Type in the message to send > ")
    print("Sending message: {:s}".format(data))

    # TCP
    # s.send(data.encode())

    # UDP
    s.sendto(data.encode(), addr)



