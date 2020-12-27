import socket
from pynput.keyboard import Listener
import platform
import select

client_TCP_socket = None


def on_press(key):
    if client_TCP_socket is not None:
        client_TCP_socket.send(key.char.encode('utf-8'))


if platform.system() == 'Windows':
    socket.SO_REUSEPORT = socket.SO_REUSEADDR

while True:
    # init sockets
    client_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    client_UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_UDP_socket.bind(("", 13117))
    print('Client started, listening for offer requests...​”.')

    data, addr = client_UDP_socket.recvfrom(1024)
    data = data.decode('utf-8')
    magic, message_type, port = data[2:10], data[10:12], data[12:16]
    if magic == 'feedbeef' and message_type == '02':
        print(f"Received offer from " + addr[0] + " attempting to connect...")
        client_TCP_socket.connect((addr[0], int(port, 16)))
        client_UDP_socket.close()

        """ selecting team name """
        data, addr = client_TCP_socket.recvfrom(1024)
        data = data.decode('utf-8')
        name = input(data)
        client_TCP_socket.send(name.encode('utf-8'))

        """ welcome message """
        data, addr = client_TCP_socket.recvfrom(1024)
        data = data.decode('utf-8')
        print(data)

        """ game starts """
        try:
            with Listener(on_press=on_press) as listener:
                while True:
                    ready = select.select([client_TCP_socket], [], [], 0.2)
                    data = None
                    if ready[0]:
                        data = client_TCP_socket.recv(1024).decode('utf-8')
                    if data is not None:
                        listener.stop()
                        break

        except KeyboardInterrupt:
            print('Exit by the user')

        """ game over message """
        # data, addr = client_TCP_socket.recvfrom(1024)
        # data = data.decode('utf-8')
        print(data)

        client_TCP_socket.close()
