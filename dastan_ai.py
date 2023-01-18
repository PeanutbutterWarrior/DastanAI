import subprocess
import re
from dataclasses import dataclass, field
from time import sleep
from enum import Enum


class Piece(Enum):
    Ryott = 'ryott'
    Chowkidar = 'chowkidar'
    Cuirassier = 'cuirassier'
    Faujdar = 'faujdar'
    Jazair = 'jazair'


@dataclass()
class Player:
    kotla: tuple[int, int] = (-1, -1)
    mirza: tuple[int, int] = (-1, -1)
    pieces: list[tuple[int, int]] = field(default_factory=list)


WIDTH = 6
HEIGHT = 6
QUEUE_SPOT_COSTS = (1, 4, 7)
moves = {
    Piece.Ryott: ((1, 0), (-1, 0), (0, 1), (0, -1)),
    Piece.Chowkidar: ((1, 1), (2, 0), (1, -1), (-1, 1), (-2, 0), (-1, -1)),
    Piece.Faujdar: ((-2, 0), (-1, 0), (1, 0), (2, 0)),
    Piece.Jazair: ((0, 2), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2)),
    Piece.Cuirassier: ((0, 2), (0, 1), (2, 1), (-2, 1)),
}


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
    p1 = Player()
    p2 = Player()
    for y, line in enumerate(grid[2:8]):
        line = iter(line)
        next(line)
        next(line)
        for x in range(6):
            assert next(line) == '|'
            kotla = next(line)
            if kotla == 'K':
                p1.kotla = (x, y)
            elif kotla == 'k':
                p2.kotla = (x, y)
            piece = next(line)
            if piece == '!':
                p1.pieces.append((x, y))
            elif piece == '"':
                p2.pieces.append((x, y))
            elif piece == '1':
                p1.mirza = (x, y)
            elif piece == '2':
                p2.mirza = (x, y)
    return p1, p2


def minimax(p1: Player,
            p2: Player,
            p1_score: int,
            p2_score: int,
            p1_move_queue: list[Piece],
            p2_move_queue: list[Piece],
            p1_turn: bool,
            depth: int):
    if depth == 0:
        return p1_score - p2_score, None
    if p1_turn:
        max_score = float('-inf')
        best_move = None
        for queue_spot in range(3):  # 3
            new_move_queue = p1_move_queue.copy()
            new_move_queue.append(new_move_queue.pop(queue_spot))
            for piece_index, piece in enumerate(p1.pieces):  # 4
                for move in moves[p1_move_queue[queue_spot]]:  # 4-7
                    x, y = piece[0] - move[0], piece[1] - move[1]
                    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                        continue
                    if (x, y) in p1.pieces or (x, y) == p1.mirza:
                        continue
                    new_score = p1_score - QUEUE_SPOT_COSTS[queue_spot]

                    taken_index = None
                    for i, other_piece in enumerate(p2.pieces):
                        if (x, y) == other_piece:
                            new_score += 1
                            taken_index = i
                    mirza_killed = False
                    if (x, y) == p2.mirza:
                        mirza_killed = True
                        new_score += 5
                    if p1.kotla in p1.pieces or p1.kotla == p1.mirza:
                        new_score += 5
                    if p2.kotla in p1.pieces or p2.kotla == p1.mirza:
                        new_score += 1

                    if taken_index:
                        new_pieces = p2.pieces.copy()
                        new_pieces.pop(taken_index)
                    else:
                        new_pieces = p2.pieces
                    new_p2 = Player(p2.kotla, p2.mirza if not mirza_killed else None, new_pieces)
                    new_pieces = p1.pieces.copy()
                    new_pieces[piece_index] = (x, y)
                    new_p1 = Player(p1.kotla, p1.mirza, new_pieces)

                    expected_score, _ = minimax(
                        new_p1,
                        new_p2,
                        new_score,
                        p2_score,
                        new_move_queue,
                        p2_move_queue,
                        False,
                        depth - 1
                    )
                    if expected_score > max_score:
                        max_score = expected_score
                        best_move = (queue_spot, piece, (x, y))
        return max_score, best_move
    else:
        min_score = float('inf')
        best_move = None
        for queue_spot in range(3):  # 3
            new_move_queue = p2_move_queue.copy()
            new_move_queue.append(new_move_queue.pop(queue_spot))
            for piece_index, piece in enumerate(p2.pieces):  # 4
                for move in moves[p2_move_queue[queue_spot]]:  # 4-7
                    x, y = piece[0] + move[0], piece[1] + move[1]
                    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                        continue
                    if (x, y) in p2.pieces or (x, y) == p2.mirza:
                        continue
                    new_score = p2_score - QUEUE_SPOT_COSTS[queue_spot]

                    taken_index = None
                    for i, other_piece in enumerate(p1.pieces):
                        if (x, y) == other_piece:
                            new_score += 1
                            taken_index = i
                    mirza_killed = False
                    if (x, y) == p1.mirza:
                        mirza_killed = True
                        new_score += 5
                    if p2.kotla in p2.pieces or p2.kotla == p2.mirza:
                        new_score += 5
                    if p1.kotla in p2.pieces or p1.kotla == p2.mirza:
                        new_score += 1

                    if taken_index:
                        new_pieces = p1.pieces.copy()
                        new_pieces.pop(taken_index)
                    else:
                        new_pieces = p1.pieces
                    new_p1 = Player(p1.kotla, p1.mirza if not mirza_killed else None, new_pieces)
                    new_pieces = p2.pieces.copy()
                    new_pieces[piece_index] = (x, y)
                    new_p2 = Player(p2.kotla, p2.mirza, new_pieces)

                    expected_score, _ = minimax(
                        new_p1,
                        new_p2,
                        p1_score,
                        new_score,
                        p1_move_queue,
                        new_move_queue,
                        True,
                        depth - 1
                    )
                    if expected_score < min_score:
                        min_score = expected_score
                        best_move = (queue_spot, piece, (x, y))
        return min_score, best_move


process = Process('Paper1_ALvl_2023_Python3_Pub_0.0.0.py')

grid = []
for _ in range(9):
    grid.append(process.readline())
p1, p2 = parse_grid(grid)

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
