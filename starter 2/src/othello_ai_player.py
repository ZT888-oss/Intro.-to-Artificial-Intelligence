import subprocess
import sys
from threading import Timer

from .othello_player import OthelloPlayer
from .othello_utils import get_score, AiTimeoutError


class OthelloAIPlayer(OthelloPlayer):
    """
    An implementation of OthelloPlayer that functions as an
    AI subprocess playing Othello.
    """

    TIMEOUT = 10 # seconds

    def __init__(
            self,
            filename: str,
            color: int,
            limit: int,
            minimax: bool = False,
            caching: bool = False,
            ordering: bool = False):
        """
        Initializes the AI player by launching the subprocess and sending its config.

        :param filename: path to the AI agent
        :param color: player's color (1 for dark, 2 for white)
        :param limit: search depth or time limit for the AI
        :param minimax: whether to use minimax algorithm
        :param caching: whether to enable caching
        :param ordering: whether to enable move ordering
        """
        self.color = color
        self.timed_out = False

        # Convert boolean flags to integers
        m, c, o = int(minimax), int(caching), int(ordering)

        try:
            # Launch AI subprocess
            self.process = subprocess.Popen(
                ['python3', filename],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )

            # Read AI name
            self.name = self.process.stdout.readline().decode("ASCII").strip()
            print(f"AI introduced itself as: {self.name}")

            # Send configuration line
            config_line = f"{color},{limit},{m},{c},{o}\n"
            self.process.stdin.write(config_line.encode("ASCII"))
            self.process.stdin.flush()
        except Exception as e:
            raise e

    def timeout(self):
        """
        Time-out when the AI takes too long to respond.
        """
        sys.stderr.write(f"{self.name} timed out.\n")
        self.process.kill()
        self.timed_out = True

    def get_move(self, manager: 'OthelloGameManager'):
        """
        Returns a tuple (row, column) representing the
        next move in the game.

        Raises an AiTimeoutError if the AI does not respond within
        the time limit.

        :param manager: game state manager containing the current board.
        """
        white_score, dark_score = get_score(manager.board)
        print((white_score, dark_score))

        # Send current score and board state
        self.process.stdin.write(f"SCORE {white_score} {dark_score}\n".encode("ASCII"))
        self.process.stdin.flush()
        self.process.stdin.write(f"{manager.board}\n".encode("ASCII"))
        self.process.stdin.flush()

        # Start timeout timer
        timer = Timer(OthelloAIPlayer.TIMEOUT, self.timeout)
        self.timed_out = False
        timer.start()

        # Read AI move
        move_s = self.process.stdout.readline().decode("ASCII")
        if self.timed_out:
            raise AiTimeoutError
        timer.cancel()

        i_str, j_str = move_s.strip().split()
        return int(i_str), int(j_str)

    def kill(self, manager: 'OthelloGameManager'):
        """
        End the game and kill the subprocess running the AI.

        :param manager: game state manager containing the current board.
        """
        white_score, dark_score = get_score(manager.board)
        self.process.stdin.write("FINAL {} {}\n".format(white_score, dark_score).encode("ASCII"))
        self.process.kill()
