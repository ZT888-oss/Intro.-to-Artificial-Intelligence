# In a new Python file or interactive console
from src.sokoban_problems import SOKOBAN_PROBLEMS
from solution import heur_manhattan_distance  # if you need your heuristic
from src.sokoban_state import SokobanState


for i, state in enumerate(SOKOBAN_PROBLEMS):
    h = heur_manhattan_distance(state)
    print(f"Problem {i}: Heuristic = {h}")

