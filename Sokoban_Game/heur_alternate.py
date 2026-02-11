from src.sokoban_problems import SOKOBAN_PROBLEMS
from solution import heur_manhattan_distance, heur_alternate

for i, state in enumerate(SOKOBAN_PROBLEMS):
    h1 = heur_manhattan_distance(state)
    h2 = heur_alternate(state)
    print(f"Problem {i}: Manhattan = {h1}, Alternate = {h2}")
