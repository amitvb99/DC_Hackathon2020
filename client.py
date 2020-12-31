import socket
import platform
import select
import msvcrt
from struct import *

client_TCP_socket = None

# socket configuration
timeout = 0.2
message_len = 1024
udp_port = 13117

# connection check
magic_cookie = 0xfeedbeef
message_type = 0x2


if platform.system() == 'Windows':
    socket.SO_REUSEPORT = socket.SO_REUSEADDR


def run_client():
    while True:
        client_TCP_socket, client_UDP_socket = init_sockets()
        data, addr = client_UDP_socket.recvfrom(message_len)
        data = unpack('IbH', data)
        magic, mtype, port = data
        if magic == magic_cookie and mtype == message_type:
            print(f"Received offer from " + addr[0] + " attempting to connect...")
            client_TCP_socket.connect((addr[0], port))
            client_UDP_socket.close()

            """ selecting team name """
            data, addr = client_TCP_socket.recvfrom(message_len)
            data = data.decode('utf-8')
            name = input(data)
            client_TCP_socket.send(name.encode('utf-8'))

            """ welcome message """
            data, addr = client_TCP_socket.recvfrom(message_len)
            data = data.decode('utf-8')
            print(data)

            """ game starts """
            try:
                get_and_send_keys(client_TCP_socket)
                client_TCP_socket.close()

            except:
                print('server disconnected')
                client_TCP_socket.close()


def init_sockets():
    """
    This function initialize the TCP and UDP sockets.
    :return:
    """
    # init sockets
    client_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    client_UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_UDP_socket.bind(("", udp_port))
    print('Client started, listening for offer requests...​”.')
    return client_TCP_socket, client_UDP_socket


def get_and_send_keys(tcp_socket):
    """
    This function receives keys from the external user, until game over message is sent from the server.
    After a game over message is received, the message is printed.

    """
    while True:
        ready = select.select([tcp_socket], [], [], timeout)
        data = None
        if ready[0]:
            data = tcp_socket.recv(message_len).decode('utf-8')
            break
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if tcp_socket is not None:
                tcp_socket.send(key)
    """ game over message """
    print(data)


if __name__ == '__main__':
    run_client()
