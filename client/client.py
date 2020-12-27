import socket
from pynput.keyboard import Listener
import platform

client_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP


def on_press(key):
    client_TCP_socket.send(key.char.encode('utf-8'))


if platform.system() == 'Windows':
    socket.SO_REUSEPORT = socket.SO_REUSEADDR

client_UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client_UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client_UDP_socket.bind(("", 13117))

while True:
    data, addr = client_UDP_socket.recvfrom(1024)
    print(f"Received offer from " + addr[0] + " attempting to connect...")

    client_TCP_socket.connect((addr[0], 12345))
    try:
        while True:
            with Listener(on_press=on_press) as listener:
                listener.join()
    except KeyboardInterrupt:
        print('Exit by the user')

    client_TCP_socket.close()

