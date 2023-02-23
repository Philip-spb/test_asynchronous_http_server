import logging
import selectors
import socket
import sys
import random

from helpers import ServerFunctions

"""
ASYNCHRONOUS WEB SERVER
"""

GRATING_LIST = [
    b'Hello, friend!\n',
    b'What\'s up?!\n',
    b'Nice to meet you!\n',
]

HOST, PORT = '', 8000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

srv_funcs = ServerFunctions()


def new_connection(selector: selectors.BaseSelector, sock: socket.socket):
    new_conn, address = sock.accept()
    logger.info('accepted new_conn from %s', address)
    new_conn.setblocking(False)
    new_conn.send(random.choice(GRATING_LIST))

    selector.register(new_conn, selectors.EVENT_READ, read_callback)


def read_callback(selector: selectors.BaseSelector, sock: socket.socket):
    data = sock.recv(1024)
    if data:
        data_str = data.decode('utf-8').strip()
        data_lst = data_str.split()
        command = data_lst[0]
        extra_data = []
        if len(data_lst) > 1:
            extra_data = data_lst[1:]
        srv_funcs.run(command, sock, extra_data=extra_data, selector=selector)
    else:
        logger.info('closing connection %s', sock)
        selector.unregister(sock)
        sock.close()


def run_iteration(selector: selectors.BaseSelector):
    events = selector.select()
    for key, mask in events:
        callback = key.data
        callback(selector, key.fileobj)


def serve_forever():
    """
    This function starts an endless listening server
    """
    with selectors.SelectSelector() as selector:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            server_socket.setblocking(False)
            logger.info('Server started on port %s', PORT)
            selector.register(server_socket, selectors.EVENT_READ, new_connection)

            while True:
                run_iteration(selector)


if __name__ == '__main__':
    serve_forever()
