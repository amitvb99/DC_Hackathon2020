import socket
import time
from _thread import *

thread_count = 0
from pynput.keyboard import Listener


def udp_socket():
    pass


def TCP_CLIENT(client_socket):
    pass


if __name__ == '__main__':
    # server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # # Enable broadcasting mode
    # server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # message = b'127.0.0.1'  #TODO change to real message
    # server_socket_udp.settimeout(0.2)
    # while True:
    #     server_socket_udp.sendto(message, ('<broadcast>', 13117))
    #     print("message sent!")
    #     time.sleep(1)

    print("Server started,listening on ip 127.0.0.1")
    server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_tcp.bind(('127.0.0.1', 12345))
    print('TCP socket wait for connection')
    server_socket_tcp.listen(4)
    client_socket, addr = server_socket_tcp.accept()
    while True:
        data = client_socket.recv(1024)
        if not data or data.decode('utf-8') == 'END':
            break
        print('received from client : %s' % data.decode('utf-8'))
    client_socket.close()