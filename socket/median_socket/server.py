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


class SimpleSocketServer:
    def __init__(self, host_config, log_level=logging.INFO):
        # Setup socket
        self.s = socket.socket()
        self.s.bind((host_config.hostname, host_config.port))
        self.s.listen(5)
        self.s.settimeout(10.0)

        # Server variables
        self.log = config_logger(self.__class__.__name__, log_level=log_level)
        self._connections=[]
        self._threads = []
        self._config = host_config
        self.running = False

    def run(self):
        self.running = True
        self.log.info('Server up, waiting for connection ... ')
        self._await_connections()

    def stop(self):
        # Server exit operation
        self.running = False
        for conn in list(self._connections):
            addr = conn.getpeername()
            self._client_hangup(conn, addr, reason='server exit')
        # TODO

    def _client_hangup(self, conn, addr, reason=None):
        if reason is None:
            self.log.info("{:}:{:} hang up.".format(addr[0], addr[1]))
        else:
            self.log.info("{:}:{:} hang up since {:}.".format(addr[0], addr[1], reason))

        conn.close()
        try:
            self._connections.remove(conn)
        except ValueError:
            return

        if self.running:
            self.log.debug('{:} live connection(s)'.format(len(self._connections)))

    def _await_connections(self):
        while self.running:
            # Accept new connection
            try:
                conn, addr = self.s.accept()
            except socket.timeout:
                continue

            if not self.validate_new_connection(conn):
                self.log.error('Failed to validate connection from {:}:{:}'.format(addr[0], addr[1]))
                conn.close()
                continue

            self._connections.append(conn)

            # Open new thread to listen client messages
            new_thread = threading.Thread(target=self._await_client_msg, args=(conn,))
            new_thread.start()
            self._threads.append(new_thread)

            self.log.info('Got connection from {:}:{:}'.format(addr[0], addr[1]))
            self.log.debug('{:} live connection(s)'.format(len(self._connections)))

    def _await_client_msg(self, conn):
        addr = conn.getpeername()
        conn.settimeout(0.5)

        while self.running:
            # Listen data from client
            try:
                # TCP
                data = conn.recv(1024)
                # # UDP
                # data = conn.recvfrom(1024)
                # data = data[0]
            except socket.timeout:
                continue
            except ConnectionResetError:
                self._client_hangup(conn, addr, reason='reset by client')
                break
            except OSError as e:
                if self.running:
                    self._client_hangup(conn, addr, reason=str(e))
                break

            # Validate if the client handup
            if len(data) == 0:
                self._client_hangup(conn, addr, reason='reset by client')
                break

            # Decode data as message
            msg = data.decode(self._config.codec)
            self.log.debug('Reviced message from {:}:{:}: {:s}'.format(addr[0], addr[1], msg))
            # self.log.debug('Binary: {:s}'.format(str(data)))
            # self.log.debug('Length: {:}'.format(len(data)))

            # Open new thread to handle client messages
            new_thread = threading.Thread(target=self.msg_callback, args=(addr, msg))
            new_thread.start()
            # self._threads.append(new_thread)

    def validate_new_connection(self, conn):
        self.log.warning('No validation for new connection (default).')
        return True

    def msg_callback(self, addr, msg):
        return msg

    def send(self, conn_idx, msg):
        if len(self._connections) > conn_idx:
            conn = self._connections[conn_idx]
            addr = conn.getpeername()
            try:
                conn.send(msg.encode(self._config.codec))
                self.log.debug('Sending to {:}:{:}: {:s}'.format(addr[0], addr[1], msg))
            except BrokenPipeError:
                self.log.error('Failed to send {:}:{:}: {:s}'.format(addr[0], addr[1], msg))

    def boardcast(self, msg):
        self.log.debug('Boardcast: {:}'.format(msg))
        for i in range(len(self._connections)):
            self.send(i, msg)


if __name__ == '__main__':
    # Get user arguments
    parser = argparse.ArgumentParser()
    config_argparser(parser)
    args = parser.parse_args()

    # Load configurations
    host_config = load_host_config(args.host_config)

    # Setup server
    my_server = SimpleSocketServer(host_config)
    my_server.run()

