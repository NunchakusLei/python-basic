import argparse
import logging
import socket
import threading
from lib import load_host_config, config_logger


def config_argparser(ap):
    ap.add_argument(
        "--host-config",
        default="config/host_config.json",
        required=False,
        help="The parth to host configuration."
    )


class SimpleSocketClient:
    def __init__(self, host_config, log_level=logging.INFO):
        # Connect to server
        self.s = socket.socket()
        self.s.connect((host_config.hostname, host_config.port))
        self.s.settimeout(0.5)

        # Client variables
        self.log = config_logger(self.__class__.__name__, log_level=log_level)
        self._config = host_config
        self.running = False

    def run(self):
        # Initialize connection
        if not self.init_connection():
           self.log.critical('Failed to initialize connection.')
           self.stop()
           return

        self.running = True
        self.recv_thread = threading.Thread(target=self._await_svr_msg)
        self.recv_thread.start()

        self._await_usr_cmd()

    def stop(self):
        self.running = False

        # Client exit operation
        # TODO

        self.log.info('Client exit.')

    def _await_usr_cmd(self):
        while self.running:
            # Get user command
            cmd = self.get_usr_cmd()

            # Open new thread to handle user command
            new_thread = threading.Thread(target=self.cmd_callback, args=(cmd,))
            new_thread.start()
            # self._threads.append(new_thread)

    def _await_svr_msg(self):
        addr = self.s.getpeername()
        while self.running:
            try:
                data = self.s.recv(1024)
            except socket.timeout:
                continue

            if len(data) == 0:
                self.log.info("{:}:{:} hang up.".format(addr[0], addr[1]))
                exit()

            msg = data.decode(self._config.codec)
            # self.log.debug('{:}:{:} say: {:}'.format(addr[0], addr[1], msg))

            # Open new thread to handle server message
            new_thread = threading.Thread(target=self.msg_callback, args=(msg,))
            new_thread.start()
            # self._threads.append(new_thread)

    def init_connection(self):
        self.log.warning('Not validation when connecting initialization (default).')
        return True

    def get_usr_cmd(self):
        cmd = input("Type in command > ")
        return cmd

    def msg_callback(self, msg):
        self.log.info('Got message: {:}'.format(msg))
        return msg

    def cmd_callback(self, cmd):
        if cmd.upper() == 'EXIT':
            self.stop()
            return
        self.send(cmd)

    def send(self, msg):
        conn = self.s
        addr = self.s.getpeername()
        try:
            data = msg.encode(self._config.codec)
            # TCP
            conn.send(data)
            # # UDP
            # conn.sendto(data, addr)
            self.log.debug('Sending message: {:}'.format(msg))
        except BrokenPipeError:
            self.log.error('Failed to send message: {:}'.format(msg))


if __name__ == '__main__':
    # Get user arguments
    parser = argparse.ArgumentParser()
    config_argparser(parser)
    args = parser.parse_args()

    # Load configurations
    host_config = load_host_config(args.host_config)

    # Setup socket
    my_client = SimpleSocketClient(host_config)
    my_client.run()

