import socket
import time
import threading
import platform
import random
import select

thread_count = 0
players_ready = 0
players_limit = 2
groups = {'Group 1': [], 'Group 2': []}
shuffle_ready = False
game_over = False
teams = {}
letters = {}
lock = threading.Lock()
restart_game = False
broadcast = True


class UdpThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        if platform.system() == 'Windows':
            socket.SO_REUSEPORT = socket.SO_REUSEADDR
        server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # server_socket_udp.bind(('', 0))
        # Enable broadcasting mode
        server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        magic_cookie = 0xfeedbeef
        message_type = 0x2
        tcp_port = 12345
        message = bytes(hex(tcp_port + (16**4)*message_type + (16**6)*magic_cookie), 'utf-8')
        server_socket_udp.settimeout(0.2)
        while broadcast:
            server_socket_udp.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
        server_socket_udp.close()

    def kill(self):
        raise SystemExit()


class TcpThread (threading.Thread):

    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        global players_ready, groups
        self.client_socket.send('Please enter your team name: '.encode('utf-8'))
        name = self.client_socket.recv(1024).decode('utf-8')
        register_team(name)
        while not shuffle_ready:
            continue
        message = """
        Welcome to Keyboard Spamming Battle Royale.\n
        Group 1:\n
        ==\n"""
        for team in groups['Group 1']:
            message += team + '\n'
        message += """
        Group 2:\n
        ==\n"""
        for team in groups['Group 2']:
            message += '\t' + team + '\n'
        message += 'Start pressing keys on your keyboard as fast as you can!!\n'
        self.client_socket.send(message.encode('utf-8'))

        while not game_over:
            ready = select.select([self.client_socket], [], [], 0.2)
            data = None
            if ready[0]:
                data = self.client_socket.recv(1024).decode('utf-8')
            if data is None:
                continue
            print('received from client : %s' % data)
            lock.acquire()
            teams[name] += 1
            if data in letters.keys():
                letters[data] += 1
            else:
                letters[data] = 1
            lock.release()

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
        Congratulations to the winners:
        """
        for team in groups[winner]:
            message += team + '\n'

        message += f"""
        Best player from each Group:\n
        Group 1:
        """

        player, score = max([item for item in teams.items() if item[0] in groups['Group 1']])
        message += player + "with a score of: " + score + "!!!\n"
        """
        Group 2:
        """
        player, score = max([item for item in teams.items() if item[0] in groups['Group 2']])
        message += player + "with a score of: " + score + "!!!\n"

        letter, times = max(letters.items())
        message += f"""
        most clicked key: {letter}, {times} times!!!\n
        """

        client_socket.send(message.encode('utf-8'))
        print(message)
        self.client_socket.close()

    def kill(self):
        raise SystemExit()


def register_team(name):
    global players_ready
    lock.acquire()
    teams[name] = 0
    players_ready += 1

    lock.release()


def reset_game():
    global thread_count, players_ready, groups, shuffle_ready, game_over, teams, letters
    thread_count = 0
    players_ready = 0
    shuffle_ready = False


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
        server_socket_tcp.bind(('192.168.56.1', 12345))
        print('TCP socket wait for connection')
        server_socket_tcp.listen(4)
        while True:
            if thread_count != players_limit:
                client_socket, addr = server_socket_tcp.accept()
                print('server accepted')
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
