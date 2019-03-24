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
    s = socket.socket()
    s.bind((host_config.hostname, host_config.port))
    s.listen(5)

    print('Server up, waiting for connection ... ')
    conn, addr = s.accept()
    print('Got connection from', addr)

    data = conn.recv(1024)
    print('Reviced message: {:s}'.format(data.decode()))



