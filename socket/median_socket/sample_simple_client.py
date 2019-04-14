import argparse
import logging
import signal
import sys
from client import SimpleSocketClient, config_argparser
from lib import load_host_config, config_logger


class MyClient(SimpleSocketClient):
    def __init__(self, host_config, client_id):
        SimpleSocketClient.__init__(self, host_config, log_level=logging.DEBUG)
        self.id = client_id
        self.passward = 'password'

    def validate_new_connection(self):
        credential = 'MyClient'  # dict(username=self.id, passward=self.passward)
        self.send(str(credential))
        if self.s.recv(1024).decode(self._config.codec) == str(credential):
            return True
        else:
            return False

    def get_usr_cmd(self):
        cmd = input("> ")
        return cmd

    def cmd_callback(self, cmd):
        msg = "id:{:}, msg:{:}".format(self.id, cmd)
        self.send(msg)

    def msg_callback(self, msg):
        self.log.debug("Got message: {:}".format(msg))


def signal_handler(signm, _frame):
    if my_client is not None:
        my_client.stop()
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

    # Setup client
    my_client = MyClient(host_config, client_id='test_client')
    my_client.run()


