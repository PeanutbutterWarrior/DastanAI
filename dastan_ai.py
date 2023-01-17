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

    def read(self, n):
        data = self.process.stdout.read(n)
        if self.echo:
            print(data, end='')
        return data

    def read_to(self, end):
        index = 0
        data = []
        while True:
            char = self.read(1)
            data.append(char)
            if char == end[index]:
                index += 1
            if index == len(end):
                break
        return ''.join(data)

    def readline(self):
        line = ''
        while not line.strip():
            if self.echo:
                print(line, end='')
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

grid = []
for _ in range(9):
    grid.append(process.readline())
p1_kotla, p1_pieces, p2_kotla, p2_pieces = parse_grid(grid)

offer = process.readline()
offer = Piece(re.match('Move option offer: (.+)\n', offer).group(1))

player = 1 if process.readline() == 'Player One\n' else 2
score = int(re.match('Score: (\d+)\n', process.readline()).group(1))
queue = [Piece(name) for name in re.findall('\d\. ([a-z]+)', process.readline())]

process.readline()
process.read_to(': ')
process.write('1')
process.read_to(': ')
process.write('22')
process.read_to(': ')
process.write('32')
