import socket
import argparse
import time
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
    addr = (host_config.hostname, host_config.port)
    s = socket.socket()
    s.connect(addr)
    log.info("Connected to server.")

    sent_msg_count = 0
    while True:
        data = input("Type in the message to send > ")
        sent_msg_count += 1

        # TCP
        # log.info("Sending message: {:s}".format(data))
        # s.send(data.encode())
        msg = "{:} {:}".format(data, sent_msg_count)
        log.info("Sending message: {:s}".format(msg))
        s.send(msg.encode())

        # # UDP
        # for i in range(10):
            # msg = "{:} {:}".format(data, i)
            # log.info("Sending message: {:s}".format(msg))
            # s.sendto(msg.encode(), addr)
            # time.sleep(1)

    s.close()


