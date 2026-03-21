"""
This module contains functions accessed by
the game manager and the game agent.

Feel free to call these functions when building your AIs.

Original Author: Daniel Bauer, Columbia University.
"""
import sys


class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass


def eprint(*args, **kwargs):
    """
    Print to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)

def find_lines(
        board: tuple[tuple[int, ...], ...],
        col: int,
        row: int,
        player: int) -> list[list[tuple[int, int]]]:
    """
    Find all uninterrupted lines of opponent stones that would be captured
    if the given player plays at (col, row).
    """
    directions = [
        (0, 1), (1, 1), (1, 0), (1, -1),
        (0, -1), (-1, -1), (-1, 0), (-1, 1)
    ]
    lines = []

    for dx, dy in directions:
        x, y = col + dx, row + dy
        line = []

        while 0 <= x < len(board) and 0 <= y < len(board):
            current = board[y][x]
            if current == 0:
                break
            elif current == player:
                if line:
                    lines.append(line)
                break
            else:
                line.append((x, y))
            x += dx
            y += dy

    return lines

def get_possible_moves(
        board: tuple[tuple[int, ...], ...],
        player: int) -> list[tuple[int, int]]:
    """
    Return a list of all possible (col, row) moves for the given player
    on the current board.
    """
    moves = []
    size = len(board)

    for col in range(size):
        for row in range(size):
            if board[row][col] == 0:
                if find_lines(board, col, row, player):
                    moves.append((col, row))

    return moves

def play_move(board: tuple[tuple[int, ...], ...],
              player: int,
              col: int,
              row: int) -> tuple[tuple[int, ...], ...]:
    """
    Return a new board resulting from the given player playing at (col, row).
    Captures all opponent pieces in valid lines.
    """
    new_board = [list(row_data) for row_data in board]
    lines = find_lines(board, col, row, player)
    new_board[row][col] = player

    for line in lines:
        for x, y in line:
            new_board[y][x] = player

    return tuple(tuple(row) for row in new_board)

def get_score(board: list[list[int]]) -> tuple[int, int]:
    """
    Return a tuple (p1_score, p2_score) representing the number of pieces
    each player has on the board.
    """
    p1_score = p2_score = 0

    for row in board:
        for cell in row:
            if cell == 1:
                p1_score += 1
            elif cell == 2:
                p2_score += 1

    return p1_score, p2_score

def play_game(game, player1, player2):
    """
    Runs a full game of Othello between two players.

    Args:
        game (OthelloGameManager): The game state manager.
        player1: Player object for dark (1).
        player2: Player object for light (2).
    """
    players = [None, player1, player2]

    while True:
        player = players[game.current_player]
        possible_moves = game.get_possible_moves()

        if not possible_moves:
            p1_score, p2_score = get_score(game.board)
            print(f"FINAL: {player1.name} (dark) {p1_score}:{p2_score} {player2.name} (light)")
            player1.kill(game)
            player2.kill(game)
            break

        color = "dark" if game.current_player == 1 else "light"

        try:
            i, j = player.get_move(game)
            print(f"{player.name} ({color}) plays {i},{j}")
            game.play(i, j)
        except AiTimeoutError:
            print(f"{player.name} ({color}) timed out!")
            p1_score, p2_score = get_score(game.board)
            print(f"FINAL: {player1.name} (dark) {p1_score}:{p2_score} {player2.name} (light)")
            player1.kill(game)
            player2.kill(game)
            break

