#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple graphical user interface for the Othello game.

Original author: Daniel Bauer, Columbia University
"""


import sys
import getopt
from tkinter import *
from tkinter import scrolledtext

# Class imports
from src import (
    OthelloGameManager,
    OthelloPlayer,
    OthelloAIPlayer,
    InvalidMoveError,
    AiTimeoutError
)

# Function imports
from src import get_possible_moves, get_score


class OthelloGui:
    """
    Graphical user interface for Othello.
    """

    def __init__(self, game_manager, player1, player2):
        """
        Initialize the GUI, players, and game board.
        """
        self.game = game_manager
        self.players = [None, player1, player2]
        self.height = self.width = self.game.dimension

        self.offset = 3
        self.cell_size = 50

        root = Tk()
        root.title("Othello")
        root.lift()
        root.attributes("-topmost", True)
        self.root = root

        self.canvas = Canvas(
            root,
            height=self.cell_size * self.height + self.offset,
            width=self.cell_size * self.width + self.offset,
        )
        self.move_label = Label(root)
        self.score_label = Label(root)
        self.text = scrolledtext.ScrolledText(root, width=70, height=10)

        self.move_label.pack(side="top")
        self.score_label.pack(side="top")
        self.canvas.pack()
        self.text.pack()

        self.draw_board()

    def get_position(self, x, y):
        """
        Convert pixel coordinates to board position.
        """
        i = (x - self.offset) // self.cell_size
        j = (y - self.offset) // self.cell_size
        return i, j

    def mouse_pressed(self, event):
        """
        Handle human player move on mouse click.
        """
        i, j = self.get_position(event.x, event.y)
        try:
            player = "Dark" if self.game.current_player == 1 else "Light"
            self.log(f"{player}: {i},{j}")
            self.game.play(i, j)
            self.draw_board()

            if not get_possible_moves(self.game.board, self.game.current_player):
                self.shutdown("Game Over")
            elif isinstance(self.players[self.game.current_player], OthelloAIPlayer):
                self.root.unbind("<Button-1>")
                self.root.after(100, self.ai_move)

        except InvalidMoveError:
            self.log(f"Invalid move. {i},{j}")

    def shutdown(self, text):
        """
        End the game and terminate any AI processes.
        """
        self.move_label["text"] = text
        self.root.unbind("<Button-1>")
        if isinstance(self.players[1], OthelloAIPlayer):
            self.players[1].kill(self.game)
        elif isinstance(self.players[2], OthelloAIPlayer):
            self.players[2].kill(self.game)

    def ai_move(self):
        """
        Make a move for the AI player.
        """
        player_obj = self.players[self.game.current_player]
        try:
            i, j = player_obj.get_move(self.game)
            player = "Dark" if self.game.current_player == 1 else "Light"
            self.log(f"{player_obj.name} {player}: {i},{j}")
            self.game.play(i, j)
            self.draw_board()

            if not get_possible_moves(self.game.board, self.game.current_player):
                self.shutdown("Game Over")
            elif isinstance(self.players[self.game.current_player], OthelloAIPlayer):
                self.root.after(1, self.ai_move)
            else:
                self.root.bind("<Button-1>", self.mouse_pressed)

        except AiTimeoutError:
            self.shutdown(f"Game Over, {player_obj.name} lost (timeout)")

    def run(self):
        """
        Start the main loop of the GUI.
        """
        if isinstance(self.players[1], OthelloAIPlayer):
            self.root.after(10, self.ai_move)
        else:
            self.root.bind("<Button-1>", self.mouse_pressed)
        self.draw_board()
        self.canvas.mainloop()

    def draw_board(self):
        """
        Redraw the entire game board and score labels.
        """
        self.draw_grid()
        self.draw_disks()
        player = "Dark" if self.game.current_player == 1 else "Light"
        self.move_label["text"] = player
        dark_score, light_score = get_score(self.game.board)
        self.score_label["text"] = f"Dark {dark_score} : {light_score} Light"

    def log(self, msg, newline=True):
        """
        Log a message to the scrollable text box.
        """
        self.text.insert("end", f"{msg}\n" if newline else msg)
        self.text.see("end")

    def draw_grid(self):
        """
        Draw the grid lines on the board.
        """
        for i in range(self.height):
            for j in range(self.width):
                x0 = i * self.cell_size + self.offset
                y0 = j * self.cell_size + self.offset
                x1 = (i + 1) * self.cell_size + self.offset
                y1 = (j + 1) * self.cell_size + self.offset
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="dark green")

    def draw_disk(self, i, j, color):
        """
        Draw a disk at a specific board position.
        """
        x = i * self.cell_size + self.offset
        y = j * self.cell_size + self.offset
        padding = 2
        self.canvas.create_oval(
            x + padding,
            y + padding,
            x + self.cell_size - padding,
            y + self.cell_size - padding,
            fill=color,
        )

    def draw_disks(self):
        """
        Draw all disks currently on the board.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.game.board[i][j] == 1:
                    self.draw_disk(j, i, "black")
                elif self.game.board[i][j] == 2:
                    self.draw_disk(j, i, "white")


def main(argv):
    size = 0
    limit = -1
    ordering = caching = minimax = False
    agent1 = agent2 = None

    try:
        opts, args = getopt.getopt(
            argv, "hcmol:d:a:b:", ["limit=", "dimension=", "agent1=", "agent2="]
        )
    except getopt.GetoptError:
        print("Usage: othello_gui.py -d <dimension> [-a <agentA> -b <agentB> -l <depth-limit> -c -o -m]")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("Usage: othello_gui.py -d <dimension> -a <agentA> [-b <agentB> -l <depth-limit> -c -o -m]")
            sys.exit()
        elif opt in ("-d", "--dimension"):
            size = int(arg)
        elif opt in ("-a", "--agentA"):
            agent1 = arg
        elif opt in ("-b", "--agentB"):
            agent2 = arg
        elif opt in ("-c", "--caching"):
            caching = True
        elif opt in ("-m", "--minimax"):
            minimax = True
        elif opt in ("-o", "--ordering"):
            ordering = True
        elif opt in ("-l", "--limit"):
            limit = int(arg)

    if size <= 0:
        print("Please provide a board size.")
        print("Usage: othello_gui.py -d <dimension> [-a <agentA> -b <agentB> -l <depth-limit> -c -o -m]")
        sys.exit(2)

    if agent1 and agent2:
        p1 = OthelloAIPlayer(agent1, 1, limit, minimax, caching, ordering)
        p2 = OthelloAIPlayer(agent2, 2, limit, minimax, caching, ordering)
    elif agent1:
        p1 = OthelloPlayer(1)
        p2 = OthelloAIPlayer(agent1, 2, limit, minimax, caching, ordering)
    else:
        p1 = OthelloPlayer(1)
        p2 = OthelloPlayer(2)

    game = OthelloGameManager(size)
    gui = OthelloGui(game, p1, p2)
    gui.run()


if __name__ == "__main__":
    main(sys.argv[1:])
