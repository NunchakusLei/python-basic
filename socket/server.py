import socket
import argparse
from lib import load_host_config, config_logger


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
    app_name = __file__.split('/')[-1].split('.')[0]
    log = config_logger(app_name)
    host_config = load_host_config(args.host_config)

    # Setup socket
    s = socket.socket()
    s.bind((host_config.hostname, host_config.port))
    s.listen(5)

    log.info('Server up, waiting for connection ... ')
    # log.error('Error')
    # log.warning('Warning')
    # log.critical('Critical')

    while True:
        conn, addr = s.accept()
        log.info('Got connection from {:}:{:}'.format(addr[0], addr[1]))
        while True:
            # conn, addr = s.accept()
            # log.info('Got connection from {:s}'.format(str(addr)))

            # TCP
            data = conn.recv(1024)
            log.debug('Reviced message from {:}:{:}: {:s}'.format(addr[0], addr[1], data.decode()))
            # log.debug('Binary: {:s}'.format(str(data)))
            # log.debug('Length: {:}'.format(len(data)))

            # UDP
            # data = conn.recvfrom(1024)
            # log.debug('Reviced message from {:}: {:s}'.format(addr, data[0].decode()))

            if len(data) == 0:
                log.info("{:}:{:} hang up.".format(addr[0], addr[1]))
                break



