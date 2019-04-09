import socket
import argparse
import threading
import time
from lib import load_host_config, config_logger

def config_argparser(ap):
    ap.add_argument(
        "--host-config",
        default="config/host_config.json",
        required=False,
        help="The parth to host configuration."
    )


class SocketClient:
    def __init__(self, host_config):
        addr = (host_config.hostname, host_config.port)
        self.config = host_config
        self.s = socket.socket()
        self.s.connect(addr)
        self.s.settimeout(1.0)
        self.active = True
        log.info("Connected to server.")

        self.sent_msg_count = 0

        self.recv_thread = threading.Thread(
            target=self.incomming_handler, args=(self.s, addr)
        )
        self.recv_thread.start()

    def send(self, msg):
        data = input("Type in the message to send > ")
        self.sent_msg_count += 1

        # TCP
        # log.info("Sending message: {:s}".format(data))
        # s.send(data.encode())
        msg = "{:} {:}".format(data, self.sent_msg_count)
        log.info("Sending message: {:s}".format(msg))
        self.s.send(msg.encode(host_config.codec))

        # # UDP
        # for i in range(10):
            # msg = "{:} {:}".format(data, i)
            # log.info("Sending message: {:s}".format(msg))
            # s.sendto(msg.encode(), addr)
            # time.sleep(1)

    def incomming_handler(self, conn, addr):
        while self.active:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                continue

            if len(data) == 0:
                log.info("{:}:{:} hang up.".format(addr[0], addr[1]))
                exit()

            log.debug('{:}:{:} say: {:}'.format(addr[0], addr[1], data.decode(self.config.codec)))
            msg = data.decode(self.config.codec)

    def hangup(self):
        self.active = False
        self.recv_thread.join()
        self.s.close()

    def message_handler(self, msg):
        return None


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
    my_client = SocketClient(host_config)
    for i in range(5):
        my_client.send("message")
    my_client.hangup()


