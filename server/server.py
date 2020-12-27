import socket
import time
import threading
import platform
from pynput.keyboard import Listener

thread_count = 0


class UdpThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        if platform.system() == 'Windows':
            socket.SO_REUSEPORT = socket.SO_REUSEADDR
        server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = b'127.0.0.1'  # TODO: change to real message
        server_socket_udp.settimeout(0.2)
        while True:
            server_socket_udp.sendto(message, ('<broadcast>', 13117))
            print("message sent!")
            time.sleep(1)


class TcpThread (threading.Thread):

    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        print('tcp thread')
        while True:
            data = self.client_socket.recv(1024)
            if not data or data.decode('utf-8') == 'END':
                break
            print('received from client : %s' % data.decode('utf-8'))
        self.client_socket.close()


if __name__ == '__main__':
    udp = UdpThread()
    udp.start()
    print("Server started,listening on ip 192.168.56.1")
    server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_tcp.bind(('192.168.56.1', 12345))
    print('TCP socket wait for connection')
    server_socket_tcp.listen(4)
    while True:
        client_socket, addr = server_socket_tcp.accept()
        tcp = TcpThread(client_socket)
        tcp.start()
