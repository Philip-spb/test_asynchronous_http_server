import socket
import time
import platform
from pathlib import Path


class ServerFunctions:
    ALL_FUNCTIONS = dict()

    def __init__(self):
        self.ALL_FUNCTIONS = {
            'quit': self._quit_function,
            'time': self._time_function,
            'info': self._info_function,
            'find': self._find_function,
        }

    def run(self, func_name: str, sock: socket.socket, *args, **kwargs):
        if func_name not in self.ALL_FUNCTIONS.keys():
            return
        func = self.ALL_FUNCTIONS[func_name]
        func(sock, *args, **kwargs)

    def _quit_function(self, sock: socket.socket, *args, selector, **kwargs):
        sock.send(bytes(f'Good by!\n', 'utf-8'))
        selector.unregister(sock)
        sock.close()

    def _time_function(self, sock: socket.socket, *args, **kwargs):
        answer = f'Current time is {time.time()}\n'
        sock.send(bytes(answer, 'utf-8'))

    def _info_function(self, sock: socket.socket, *args, **kwargs):
        platform_info = platform.uname()
        python_version = platform.python_version()
        answer = f'Platform version: {platform_info}\nPython version: {python_version}\n'
        sock.send(bytes(answer, 'utf-8'))

    def _find_function(self, sock: socket.socket, *args, extra_data: list, **kwargs):
        if not len(extra_data):
            return

        file_name = extra_data[0]
        paths = sorted(Path('.').glob(f'*{file_name}*'))

        if not len(paths):
            return

        for file in paths:

            if file.is_dir():
                continue

            stat = file.stat()
            file_inf = f'file name: {file.name}\n'
            file_inf += f'file size: {stat.st_size}\n'
            file_inf += f'file creation date: {stat.st_ctime}\n'
            sock.send(bytes(file_inf, 'utf-8'))
            sock.send(bytes('-' * 30, 'utf-8'))
            sock.send(bytes('\n', 'utf-8'))
