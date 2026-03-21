from .othello_utils import (
    InvalidMoveError,
    find_lines,
    play_move,
    get_possible_moves
)


class OthelloGameManager:
    """
    Manages game state for an Othello match, including board state,
    current player, and valid moves.
    """

    def __init__(self, dimension: int = 6):
        """
        Initializes a new Othello game.

        :param dimension: size of the square board (default is 6)
        """
        self.dimension = dimension
        self.board = self.create_initial_board()
        self.current_player = 1

    def create_initial_board(self) -> tuple[tuple[int, ...], ...]:
        """
        Return an initial Othello board with 4 pieces in the center.
        """
        board = [[0 for _ in range(self.dimension)] for _ in range(self.dimension)]

        mid = self.dimension // 2 - 1
        board[mid][mid] = 2
        board[mid + 1][mid + 1] = 2
        board[mid + 1][mid] = 1
        board[mid][mid + 1] = 1

        return tuple(tuple(row) for row in board)

    def print_board(self):
        """
        Print the current board state to stdout.
        """
        for row in self.board:
            print(" ".join(map(str, row)))

    def play(self, i: int, j: int):
        """
        Play a move at (i, j).

        Raise an InvalidMoveError if the position is occupied,
        or if the move is invalid.

        :param i: column index
        :param j: row index
        """
        if self.board[j][i] != 0:
            raise InvalidMoveError("Occupied square.")

        lines = find_lines(self.board, i, j, self.current_player)
        if not lines:
            raise InvalidMoveError("Invalid move.")

        self.board = play_move(self.board, self.current_player, i, j)
        self.current_player = 2 if self.current_player == 1 else 1

    def get_possible_moves(self) ->list[tuple[int, int]]:
        """
        Returns a list of valid moves for the current player.

        Returns:
            list: Valid (i, j) move positions.
        """
        return get_possible_moves(self.board, self.current_player)
