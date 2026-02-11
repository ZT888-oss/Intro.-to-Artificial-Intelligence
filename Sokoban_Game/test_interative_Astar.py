from src.sokoban_problems import SOKOBAN_PROBLEMS
from solution import iterative_astar, heur_manhattan_distance

initial_weight = 10
timebound = 60  # seconds

for i, problem in enumerate(SOKOBAN_PROBLEMS):
    print(f"\n=== Problem {i} ===")
    
    # Run iterative A* with a starting weight
    goal, stats = iterative_astar(problem, heur_manhattan_distance, weight=initial_weight, timebound=timebound)
    
    if goal:
        print(f"Iterative Weighted A*: SUCCESS | Cost = {goal.gval} | Time = {stats.total_time:.4f}s | Nodes expanded = {stats.states_expanded}")
    else:
        print(f"Iterative Weighted A*: FAILED | Time = {stats.total_time:.4f}s | Nodes expanded = {stats.states_expanded}")
