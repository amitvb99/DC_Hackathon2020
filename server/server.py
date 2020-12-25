import threading
from client import client


class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.score = 0

    def run(self):
        pass

    def update_score(self):
        self.score += 1



if __name__ == '__main__':
    pass
