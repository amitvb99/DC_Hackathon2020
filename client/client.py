import socket
from pynput.keyboard import Listener

server = None
counter = 0


def look_for_server(host, port):
    print("Client started, listening for offer requests...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    while True:
        s.listen(5)
        break
    connect_to_server(s)


def connect_to_server(s):
    # print(f'Received offer from {}, attempting to connect')
    global server
    server, addr = s.accept()
    while True:
        break
    game_mode()


def game_mode():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def on_press(key):
    global server
    server.send(f'{key} pressed')
    # global counter
    # counter += 1
    # print(counter)


def on_release(key):
    pass


if __name__ == "__main__":
    # HOST = '127.0.0.1'
    # PORT = 65432
    # while True:
    #     look_for_server(HOST, PORT)
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
