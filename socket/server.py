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


class SocketServer:
    def __init__(self, host_config):
        # Setup socket
        self.s = socket.socket()
        self.s.bind((host_config.hostname, host_config.port))
        self.s.listen(5)

        self.connections=[]
        self.threads = []
        self.config = host_config

        log.info('Server up, waiting for connection ... ')
        # log.error('Error')
        # log.warning('Warning')
        # log.critical('Critical')
        while True:
            # Accept new connection
            conn, addr = self.listening()

            # Open new thread to handle client messages
            new_thread = threading.Thread(
                target=self.client_handler, args=(conn, addr)
            )
            new_thread.start()
            self.threads.append(new_thread)

    def listening(self):
        conn, addr = self.s.accept()
        self.connections.append((conn, addr))
        log.info('Got connection from {:}:{:}'.format(addr[0], addr[1]))
        log.debug('{:} live connection(s)'.format(len(self.connections)))
        return conn, addr

    def client_handler(self, conn, addr):
        while True:
            # TCP
            data = conn.recv(1024)
            # # UDP
            # data = conn.recvfrom(1024)
            # data = data[0]

            if len(data) == 0:
                log.info("{:}:{:} hang up.".format(addr[0], addr[1]))
                self.connections.remove((conn, addr))
                log.debug('{:} live connection(s)'.format(len(self.connections)))
                break

            log.debug('Reviced message from {:}:{:}: {:s}'.format(addr[0], addr[1], data.decode(self.config.codec)))
            # log.debug('Binary: {:s}'.format(str(data)))
            # log.debug('Length: {:}'.format(len(data)))
            msg = data.decode(self.config.codec)

            response = self.message_handler(msg)
            if response is not None:
                conn.send(response.encode(self.config.codec))

    def message_handler(self, msg):
        return msg

    def boardcast(self, msg):
        for connection in self.connections:
            conn = connection[0]
            addr = conn.getpeername()
            try:
                conn.send(msg.encode(self.config.codec))
                log.debug('Sending to {:}:{:}: {:s}'.format(addr[0], addr[1], msg))
            except BrokenPipeError:
                log.error('Failed to send {:}:{:}: {:s}'.format(addr[0], addr[1], msg))


if __name__ == '__main__':
    # Get user arguments
    parser = argparse.ArgumentParser()
    config_argparser(parser)
    args = parser.parse_args()

    # Load configurations
    app_name = __file__.split('/')[-1].split('.')[0]
    log = config_logger(app_name)
    host_config = load_host_config(args.host_config)

    # Setup server
    my_server = SocketServer(host_config)


