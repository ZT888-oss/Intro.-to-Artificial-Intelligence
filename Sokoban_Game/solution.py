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

def check_obstcale(state: 'SokobanState', box: tuple[int, int]) -> bool:
   x,y = box
   obstale = state.obstacles

   left = ((x-1,y) in obstale)or(x-1<0) 
   right = ((x+1, y)in obstale) or (x+1>=state.width)
   top = ((x,y+1) in obstale) or (y-1<0)
   bottom = ((x, y-1) in obstale) or (y+1 >= state.height)

   if(right and top) or (right and bottom) or (left and top) or (left and bottom):
       return True
   return False

def is_blocked(x, y, state, boxes):
    if x < 0 or x >= state.width or y < 0 or y >= state.height:
        return True
    if (x, y) in state.obstacles:
        return True
    if (x, y) in boxes:
        return True

    return False

def box_is_frozen(box, state, boxes):
    x, y = box
    # never deadlock storage
    if box in state.storage:
        return False

    left  = is_blocked(x-1, y, state, boxes)
    right = is_blocked(x+1, y, state, boxes)
    up    = is_blocked(x, y-1, state, boxes)
    down  = is_blocked(x, y+1, state, boxes)
    left_up = is_blocked(x-1, y-1, state, boxes)
    right_up = is_blocked(x+1, y-1, state, boxes)
    left_down = is_blocked(x-1, y+1, state, boxes)
    right_down = is_blocked(x+1, y+1, state, boxes)

    # cannot move horizontally AND vertically
    if((left and left_up and up) or (up and right and right_up) or (down and right and right_down) or (left and up and left_up)):
        return True
    
    return False

# def check_box_deadlock(state: 'SokobanState', box: tuple[int, int]) -> bool:
#     x, y = box
#     obstale = state.obstacles
#     '''
#     w b
#     w b
#     '''
#     if ((x-1<0) and (x, y-1)in box):
#         return True
#     # ob
#     # bb
#     if (((x-1, y-1) in obstale)and ((x-1,y) in box )and ((x, y-1) in box)):
#         return True
#     # BB
#     # BB
#     if (((x-1,y) in box) and ((x-1,y-1) in box) and ((x, y-1) in box)):
#         return True
#     # BB
#     # OB
#     if ((x-1,y) in obstale) and ((x-1, y-1) in box) and ((x, y-1) in box):
#         return True
#     # BB
#     # BO
#     if((x+1, y+1) in box) and ((x, y+1) in box) and ((x+1, y+1)in obstale):
#         return True
#     return False
# SOKOBAN HEURISTICS
def heur_alternate(state: 'SokobanState') -> float:
    """
#     Returns a heuristic value with the goal of improving upon
#     the flaws inherent to a heuristic that uses Manhattan distance
#     and produce a more accurate estimate of the distance from the
#     current state to the goal state.

#     You must explain your heuristic via inline comments.

#     :param state: A SokobanState object representing the current
#                   state in a game of Sokoban.
#     :return: An estimate of the distance from the current
#              SokobanState to the goal state.
#     """
#     # TODO: IMPLEMENT
    import heapq
    import math

    boxes = list(state.boxes)
    storage = list(state.storage)
    robots = state.robots
    optimal_dis = 0

    assigned_storage = set()  # storage indices already assigned

    # --- Box → Storage assignment (greedy) ---
    unassigned_boxes = set(range(len(boxes)))
    #check the case: 
    box_counts = {
        'left': 0, 'right': 0,
        'top': 0, 'bottom': 0
    }

    storage_counts = {
        'left': 0, 'right': 0,
        'top': 0, 'bottom': 0
    }
        
    for box in boxes:
        x, y = box
        if box not in storage:
            # Box in a corner (unsolvable if not on storage)
            if ((x == 0 or x == state.width - 1) and
                (y == 0 or y == state.height - 1)):
                return math.inf
            # Box along the wall but no storage along that wall
            if x == 0 or x == state.width - 1:
                if not any(s[0] == x for s in storage):
                    return math.inf
            if y == 0 or y == state.height - 1:
                if not any(s[1] == y for s in storage):
                    return math.inf
            # Optional: check if box is surrounded by obstacles
            if check_obstcale(state, box):
                 return math.inf
            if box_is_frozen(box, state, boxes):
                return math.inf
    # Count boxes along walls
    for box in boxes:
        x, y = box
        if x == 0:
            box_counts['left'] += 1
        if x == state.width - 1:
            box_counts['right'] += 1
        if y == 0:
            box_counts['top'] += 1
        if y == state.height - 1:
            box_counts['bottom'] += 1

    # Count storage along walls
    for s in storage:
        x, y = s
        if x == 0:
            storage_counts['left'] += 1
        if x == state.width - 1:
            storage_counts['right'] += 1
        if y == 0:
            storage_counts['top'] += 1
        if y == state.height - 1:
            storage_counts['bottom'] += 1

    # Check for impossible situation
    for n in ['left', 'right', 'top', 'bottom']:
        if box_counts[n] > storage_counts[n]:
            return math.inf    
        
    while unassigned_boxes:
        heap = []
        for b_idx in unassigned_boxes:
            box = boxes[b_idx]
            for s_idx, s in enumerate(storage):
                if s_idx in assigned_storage: # if storage already hold a box, ignore it
                    continue
                #if both box and storage is avaiable:
                dist = abs(box[0] - s[0]) + abs(box[1] - s[1])
                heapq.heappush(heap, (dist, b_idx, s_idx))
        #safe check
        if heap:
            dist, b_idx, s_idx = heapq.heappop(heap)
            optimal_dis += dist
            assigned_storage.add(s_idx)
            unassigned_boxes.remove(b_idx)

    robot = state.robots
    for r in robot:
        min_dist = float('inf')
        for box in boxes:
             dist = abs(box[0] - r[0]) + abs(box[1] - r[1])
             if dist < min_dist:
                min_dist = dist
        
        optimal_dis += min_dist

    return optimal_dis

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
    #raise NotImplementedError("You must implement heur_manhattan_distance.")
    total_dis = 0
    for box in state.boxes:
        # find neareast storage point to current box
        dis = min(abs(box[0] - storage[0])+ abs(box[1] - storage[1]) for storage in state.storage) # 0 repersent x corredinate, 1 repesent y corrdinate (they are stored in tuple)
        total_dis += dis

    return total_dis
    

def fval_function(node: 'SearchNode', weight: float) -> float:
    """
    Returns the f-value of the state contained in node
    based on weight, to be used in Anytime Weighted A* search.

    :param node: A SearchNode object containing a SokobanState object
    :param weight: The weight used in Anytime Weighted A* search.
    :return: The f-value of the state contained in node.
    """
    # TODO: IMPLEMENT
    return node.gval + weight*node.hval
    #raise NotImplementedError("You must implement fval_function.")

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
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    engine = SearchEngine(strategy='custom', cc='full')
    engine.init_search(
       init_state = initial_state,
        goal_fn = sokoban_goal_state,
        heur_fn = heur_fn,
        fval_fn =wrapped_fval_function
    )
    goal_state, stats = engine.search(timebound=timebound)
    return goal_state, stats
    #raise NotImplementedError("You must implement weighted_astar.")

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

    start_time = os.times()[0]
    best_solution = False
    best_cost = float('inf')
    best_stat = SearchStatistics(0, 0, 0, 0, 0)

    time_left = timebound
    current_weight = weight
    
    while time_left > 0:
        result, stat = weighted_astar(
            initial_state,
            heur_fn,
            current_weight,
            time_left
        )

        if not result:
            break
        if result:
            if result.gval < best_cost:
                best_solution = result
                best_cost = result.gval
                best_stat = stat

        # decrease weight toward optimal A*
        current_weight = max(1, current_weight * 0.85)

        # update remaining time
        time_left = timebound - (os.times()[0] - start_time)

    return best_solution, best_stat

    #raise NotImplementedError("You must implement iterative_astar.")

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
    best_solution = None
    best_stat = None
    best_cost = float('inf')

    start_time = os.times()[0]
    time_left = timebound
    while(1):
        # update remaining time
        time_left = timebound - (os.times()[0] - start_time)

        if time_left <= 0:
            break

        if time_left > 0:
            engine = SearchEngine(strategy='best_first')
            engine.init_search(
                init_state=initial_state,
                goal_fn=sokoban_goal_state,
                heur_fn=heur_fn
            )

            solution, stats = engine.search(
                timebound=time_left,
                costbound=(best_cost, float('inf'), float('inf'))  # prune on g only
            )

            if solution:
                if solution.gval < best_cost:
                    best_solution = solution
                    best_cost = solution.gval
                    best_stat = stats

    if best_solution:
        return best_solution, best_stat
    else:
        return False, SearchStatistics(0,0,0,0,0)