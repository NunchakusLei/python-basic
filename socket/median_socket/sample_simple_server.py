import argparse
import logging
import signal
import sys
from server import SimpleSocketServer, config_argparser
from lib import load_host_config, config_logger


class MyServer(SimpleSocketServer):
    def __init__(self, host_config):
        SimpleSocketServer.__init__(self, host_config, log_level=logging.DEBUG)

    def validate_new_connection(self, conn):
        handshake_msg = conn.recv(1024).decode(self._config.codec)
        if handshake_msg == 'MyClient':
            conn.send(handshake_msg.encode(self._config.codec))
            return True
        else:
            return False

    def msg_callback(self, addr, msg):
        self.boardcast(msg)


def signal_handler(signm, _frame):
    if my_server is not None:
        my_server.stop()
    log.info("Got signal {:}, exiting now".format(signm))
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGABRT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get user arguments
    parser = argparse.ArgumentParser()
    config_argparser(parser)
    args = parser.parse_args()

    # Load configurations
    app_name = __file__.split('/')[-1].split('.')[0]
    log = config_logger(app_name, logging.DEBUG)
    host_config = load_host_config(args.host_config)

    # Setup server
    # my_server = SimpleSocketServer(host_config)
    my_server = MyServer(host_config)
    my_server.run()


