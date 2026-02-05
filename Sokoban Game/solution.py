#   You may only add standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files
from typing import Callable, Union

import os                       # For time functions
import math                     # For infinity

from src import (
    # For search engine implementations
    SearchEngine, SearchNode, SearchStatistics,
    # For Sokoban-specific implementations
    SokobanState,
    sokoban_goal_state,
    UP, DOWN, LEFT, RIGHT,
    # You may further import any constants you may need.
    # See `search_constants.py`
)

# SOKOBAN HEURISTICS
def heur_alternate(state: 'SokobanState') -> float:
    """
    Returns a heuristic value with the goal of improving upon
    the flaws inherent to a heuristic that uses Manhattan distance
    and produce a more accurate estimate of the distance from the
    current state to the goal state.

    You must explain your heuristic via inline comments.

    :param state: A SokobanState object representing the current
                  state in a game of Sokoban.
    :return: An estimate of the distance from the current
             SokobanState to the goal state.
    """
    # TODO: IMPLEMENT
    raise NotImplementedError("You must implement heur_alternate.")

def heur_zero(state: 'SokobanState') -> float:
    """
    This function is used in A* to perform a uniform cost search
    by returning zero.

    :param state: A SokobanState object representing the current
                  state in a game of Sokoban.
    :return: The zero value.
    """
    return 0

def heur_manhattan_distance(state: 'SokobanState') -> float:
    # IMPLEMENT
    """
    Returns an admissible - i.e. optimistic - heuristic by never
    overestimating the cost to transition from the current state to the goal state.
    The sum of the Manhattan distances between each box that has yet to be stored
    and the storage point nearest to it qualifies as such a heuristic.

    You may assume there are no obstacles on the grid when calculating distances.
    You must implement this function exactly as specified.

    :param state: A SokobanState object representing the current
                  state in a game of Sokoban.
    :return: An admissible estimate of the distance from the
             current SokobanState to the goal state.
    """
    # TODO: IMPLEMENT
    raise NotImplementedError("You must implement heur_manhattan_distance.")

def fval_function(node: 'SearchNode', weight: float) -> float:
    """
    Returns the f-value of the state contained in node
    based on weight, to be used in Anytime Weighted A* search.

    :param node: A SearchNode object containing a SokobanState object
    :param weight: The weight used in Anytime Weighted A* search.
    :return: The f-value of the state contained in node.
    """
    # TODO: IMPLEMENT
    raise NotImplementedError("You must implement fval_function.")

# SEARCH ALGORITHMS
def weighted_astar(
        initial_state: 'SokobanState',
        heur_fn: Callable,
        weight: float,
        timebound: int) -> tuple[Union['SokobanState', bool], 'SearchStatistics']:
    """
    Returns a tuple of the goal SokobanState and a SearchStatistics object
    by implementing weighted A* search as defined in the handout.

    If no goal state is found, returns a tuple of False and a SearchStatistics
    object.

    :param initial_state: The initial SokobanState of the game of Sokoban.
    :param heur_fn: The heuristic function used in weighted A* search.
    :param weight: The weight used in calculating the heuristic.
    :param timebound: The time bound used in weighted A* search, in seconds.
    :return: A tuple consisting of the goal SokobanState or False if such a state
             is not found, and a SearchStatistics object.
    """
    # TODO: Implement
    raise NotImplementedError("You must implement weighted_astar.")

def iterative_astar( # uses f(n)
        initial_state: 'SokobanState',
        heur_fn: Callable,
        weight: float = 1,
        timebound: int = 5) -> tuple[Union['SokobanState', bool], 'SearchStatistics']:
    """
    Returns a tuple of the goal SokobanState and a SearchStatistics object
    by implementing realtime iterative A* search as defined in the handout.

    If no goal state is found, returns a tuple of False and a SearchStatistics
    object.

    Refer to test_alternate_fun in autograder.py to see how to initialize a search.

    :param initial_state: The initial SokobanState of the game of Sokoban.
    :param heur_fn: The heuristic function used in realtime iterative A* search.
    :param weight: The weight used in calculating the heuristic.
    :param timebound: The time bound used in realtime iterative A* search, in seconds.
    :return: A tuple consisting of the goal SokobanState or False if such a state
             is not found, and a SearchStatistics object.
    """
    # TODO: IMPLEMENT
    raise NotImplementedError("You must implement iterative_astar.")

def iterative_gbfs( # uses h(n)
        initial_state: 'SokobanState',
        heur_fn: Callable,
        timebound: int = 5) -> tuple[Union['SokobanState', bool], 'SearchStatistics']:
    """
    Returns a tuple of the goal SokobanState and a SearchStatistics object
    by implementing iterative greedy best-first search as defined in the handout.

    :param initial_state: The initial SokobanState of the game of Sokoban.
    :param heur_fn: The heuristic function used in iterative greedy best-first search.
    :param timebound: The time bound used in iterative greedy best-first search, in seconds.
    :return: A tuple consisting of the goal SokobanState or False if such a state
             is not found, and a SearchStatistics object.
    """
    # TODO: IMPLEMENT
    raise NotImplementedError("You must implement iterative_gbfs.")
