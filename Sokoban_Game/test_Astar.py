from src.sokoban_problems import SOKOBAN_PROBLEMS
from solution import weighted_astar, heur_manhattan_distance

weights = [10, 5, 2, 1]
timebound = 60  # seconds

for i, problem in enumerate(SOKOBAN_PROBLEMS):
    print(f"\n=== Problem {i} ===")
    for w in weights:
        goal, stats = weighted_astar(problem, heur_manhattan_distance, weight=w, timebound=timebound)
        
        if goal:
            print(f"Weight {w}: SUCCESS | Cost = {goal.gval} | Time = {stats.total_time:.4f}s | Nodes expanded = {stats.states_expanded}")
        else:
            print(f"Weight {w}: FAILED | Time = {stats.total_time:.4f}s | Nodes expanded = {stats.states_expanded}")
