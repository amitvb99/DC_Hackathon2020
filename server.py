import socket
import time
import threading
import platform
import random
import select
from struct import *

# socket configuration
timeout = 0.2
message_len = 1024
tcp_port = 12345
ip_address = '192.168.56.1'

# game configuration
thread_count = 0
players_ready = 0
players_limit = 2
groups = {'Group 1': [], 'Group 2': []}
teams = {}
letters = {}

# conditions
shuffle_ready = False
game_over = False
restart_game = False
broadcast = True

# lock for shared variables
lock = threading.Lock()


class UdpThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.magic_cookie = 0xfeedbeef
        self.message_type = 0x2
        self.tcp_port = tcp_port

    def run(self):
        if platform.system() == 'Windows':
            socket.SO_REUSEPORT = socket.SO_REUSEADDR
        server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Enable broadcasting mode
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = pack('IbH', self.magic_cookie, self.message_type, self.tcp_port)
        server_socket_udp.settimeout(timeout)
        while broadcast:
            server_socket_udp.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
        server_socket_udp.close()


class TcpThread (threading.Thread):

    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        global players_ready, groups
        self.client_socket.send('Please enter your team name: '.encode('utf-8'))
        name = self.client_socket.recv(message_len).decode('utf-8')
        register_team(name)
        while not shuffle_ready:
            continue
        welcome = welcome_message()
        self.client_socket.send(welcome.encode('utf-8'))

        while not game_over:
            ready = select.select([self.client_socket], [], [], timeout)
            data = None
            if ready[0]:
                data = self.client_socket.recv(message_len).decode('utf-8')
            if data is None:
                continue
            # print('received from client : %s' % data)
            lock.acquire()
            teams[name] += 1
            if data in letters.keys():
                letters[data] += 1
            else:
                letters[data] = 1
            lock.release()

        message = game_over_message()
        send_tcp_message(message, self.client_socket)
        print(message)
        self.client_socket.close()


def register_team(name):
    """
    This function registers a new team to the current game.
    :param name: The name of the team to register.
    :return:
    """
    global players_ready
    lock.acquire()
    teams[name] = 0
    players_ready += 1

    lock.release()


def reset_game():
    """
    This function resets all the game control variables, to get ready for a new upcoming game.
    :return:
    """
    global thread_count, players_ready, groups, shuffle_ready, game_over, teams, letters
    thread_count = 0
    players_ready = 0
    shuffle_ready = False


def welcome_message():
    """
    This function generates the welcome message needed to be sent to all clients.
    :return: the welcome message
    """
    message = """
            Welcome to Keyboard Spamming Battle Royale.\n
            """
    message += group_members('Group 1')
    message += group_members('Group 2')
    message += 'Start pressing keys on your keyboard as fast as you can!!\n'
    return message


def group_members(group_name):
    """
    This function generates a string describing {group_name}.
    The string includes the group name as a  header, and a list of all the teams in {group_name}
    :param group_name: the name of the group to generate a string for.
    :return: A string describing {group_name}
    """
    group = f'{group_name}:\n===\n'
    for team in groups[group_name]:
        group += f'{team}\n'
    return group


def best_player(group_name):
    """
    This function generates a string of the best player from {group_name}.
    The string includes the group name as a  header, and the name of the player with the highest
    score together with its score during the game.
    :param group_name: The name of the group to print its best player.
    :return:
    """
    message = f'{group_name}\n:'
    group_scores = [item for item in teams.items() if item[0] in groups[group_name]]
    if len(group_scores) is 0:
        message += "NO PLAYERS\n"
    else:
        player, score = max(group_scores)
        message += f"{player} with a score of: {score}!!!\n"
    return message


def key_stats():
    """
    This function generates a string with statistic about the most clicked key during
    a specific game.
    :return: The generated string
    """
    message = ""
    if len(letters.items()) is 0:
        message += "NO KEYS SENT!!"
    else:
        letter, times = max(letters.items())
        message += f"""
        most clicked key: {letter}, {times} times!!!\n
        """
    return message


def game_over_message():
    """
    This function generates the game over message needed to be sent to all clients.
    The message includes the score of the game and the winning group, best player from each group
    and statistics about the keys clicked during the game.
    :return: The game over message
    """
    group1_score = sum([teams[team] for team in groups['Group 1']])
    group2_score = sum([teams[team] for team in groups['Group 2']])
    if group2_score < group1_score:
        winner = 'Group 1'
    else:
        winner = 'Group 2'

    message = f"""
            Game Over!\n
            Group 1 typed in {group1_score} characters, Group 2 typed in {group2_score} characters.\n
            {winner} wins!\n
            \n
            Congratulations to the winners:"""
    message += group_members(winner)

    message += f"""
            Best player from each Group:\n
            """
    message += best_player('Group 1')
    message += best_player('Group 2')

    message += key_stats()
    return message


def send_tcp_message(message, tcp_socket):
    """
    This function sends {message} to the client using {tcp_socket}.
    :param message: the message to send
    :param tcp_socket: the socket we use to send the message.
    :return:
    """
    lock.acquire()
    tcp_socket.send(message.encode('utf-8'))
    lock.release()


if __name__ == '__main__':
    while True:
        reset_game()
        udp = UdpThread()
        udp.start()
        if restart_game:
            print("​Game over, sending out offer requests...")
        else:
            print("Server started,listening on IP address 192.168.56.1")
        server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_tcp.bind((ip_address, tcp_port))
        print('TCP socket wait for connection')
        server_socket_tcp.listen(4)
        while True:
            if thread_count != players_limit:
                client_socket, addr = server_socket_tcp.accept()
                if restart_game:
                    restart_game = False
                    groups = {'Group 1': [], 'Group 2': []}
                    game_over = False
                    teams = {}
                    letters = {}
                tcp = TcpThread(client_socket)
                tcp.start()
                lock.acquire()
                thread_count += 1
                lock.release()

            if players_ready == players_limit:
                broadcast = False
                lst = list(teams.keys())
                random.shuffle(lst)
                groups['Group 1'], groups['Group 2'] = lst[:int(len(lst) / 2)], lst[int(len(lst) / 2):]
                shuffle_ready = True
                start_time = time.time()
                while time.time() < start_time + 10:
                    continue
                game_over = True
                break

        restart_game = True
        broadcast = True
