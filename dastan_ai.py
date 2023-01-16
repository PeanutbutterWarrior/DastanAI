import subprocess
import re
import random
from pprint import pprint
from time import sleep


class Process:
    def __init__(self, filename, echo=True):
        self.process = subprocess.Popen(['python', filename],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        encoding='utf-8')
        self.echo = echo

    def readline(self):
        line = self.process.stdout.readline()
        if self.echo:
            print(line, end='')
        return line

    def write(self, data, delay=True):
        if self.echo:
            print(data)
        self.process.stdin.write(data)
        self.process.stdin.write('\n')
        self.process.stdin.flush()
        if delay:
            sleep(0.05)  # Delay to let the program proceed


def parse_grid(grid):
    p1_kotla = None
    p2_kotla = None
    p1_pieces = []
    p2_pieces = []
    for y, line in enumerate(grid[2:8]):
        line = iter(line)
        next(line)
        next(line)
        for x in range(6):
            assert next(line) == '|'
            kotla = next(line)
            if kotla == 'K':
                p1_kotla = (x, y)
            elif kotla == 'k':
                p2_kotla = (x, y)
            piece = next(line)
            if piece == '!':
                p1_pieces.append((x, y))
            elif piece == '"':
                p2_pieces.append((x, y))
    return p1_kotla, p1_pieces, p2_kotla, p2_pieces


process = Process('Paper1_ALvl_2023_Python3_Pub_0.0.0.py')
process.readline()

grid = []
for _ in range(9):
    grid.append(process.readline())
print(parse_grid(grid))
