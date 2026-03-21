from typing import Callable, Optional

# These functions are imported for you to use
# in your implementation.
from src import (
    find_lines,
    get_possible_moves,
    get_score,
    play_move,
    eprint      # for debugging
)

# Use this global variable for state caching.
# You may find that it's useful to use the following
# information to form a key into the
#
# key = (board, player_to_move, limit, node_type)
#
state_cache = {}


###############################################################################
############################# VALUE FUNCTIONS #################################
###############################################################################
def compute_utility(board: tuple[tuple[int, ...], ...], color: int) -> int:
    """
    Return the utility value of the given board for the given player color.

    :param board: a board representing the current state of an Othello game
    :param color: the color of the player. 1 for dark, 2 for light.

    :return: the utility of the given board for the given player color.
    """
    dark_socre, light_socre = get_score(board)
    if color == 1:
        return dark_socre - light_socre
    elif color == 2:
        return light_socre - dark_socre

def compute_heuristic(board: tuple[tuple[int, ...], ...], color: int) -> int:
    """
    Return the heuristic value of the given board for the given player color.

    :param board: a board representing the current state of an Othello game
    :param color: the color of the player. 1 for dark, 2 for light.

    :return: the heuristic value of the given board for the given player color.
    """
    # TODO: Implement
    opponent = 2 if color == 1 else 1 

    #pieces difference:
    my_disk = 0
    opponent_disk = 0
    
    for row in board:
        for cell in row:
            if cell == color:
                my_disk += 1
            elif cell == opponent:
                opponent_disk += 1
    disk_score = my_disk - opponent_disk
    
    #number of moves available to you versus your opponent.
    my_moves = len(get_possible_moves(board, color))
    opp_moves = len(get_possible_moves(board, opponent))
    mobility_score = my_moves - opp_moves
    
    size = len(board)
    #Consider board locations where pieces are stable (i.e., cannot be flipped).
    #corner cannot be flipped
    corners = [(0, 0),
        (0, size - 1),
        (size - 1, 0),
        (size - 1, size - 1)]
    
    my_corner = 0
    opponent_corner = 0
    
    for i, j in corners:
        if board[j][i] == color:
            my_corner +=1
        elif board[j][i] == opponent:
            opponent_corner +=1
    corner_score = my_corner - opponent_corner
    
    #Empirical Tuning according general Othello game(weighr distribution we assume (1, 3, 25))
    return 1*disk_score+3*mobility_score+25*corner_score
            

###############################################################################
####################### ALPHA-BETA PRUNING FUNCTIONS ##########################
###############################################################################
def alphabeta_min_node(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        alpha: int,
        beta: int,
        limit: int,
        caching: int = 0,
        ordering: int = 0) -> tuple[Optional[tuple[int, int]], int]:
    """
    Return a tuple of the move that yields the *lowest* possible utility
    and the *lowest* possible utility itself for the given board, color,
    limit, value_fn to determine utility and alpha, beta to prune.
    Optionally use state caching and node ordering.

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param alpha: the alpha parameter, used in pruning
    :param beta: the beta parameter, used in pruning
    :param limit: the depth limit of the alpha-beta search
    :param caching: whether to use state caching
                    if 1, use state caching
                    if 0, do not use state caching
    :param ordering: whether to order moves during move selection

    :return: a tuple (None|(i,j), utility) of the next move to be
             taken, and the utility value associated with it
    """
    # TODO: Implement
    if limit == 0:
        return None, value_fn(board, color)

    key = (board, color, limit)
    #avoid regenerating same board
    if caching and key in state_cache:
        return state_cache[key]

    opponent = 2 if color == 1 else 1
    moves = get_possible_moves(board, opponent)

    # Terminal state
    if not moves:
        return None, value_fn(board, color)

    best_value = float('inf')
    best_move = None
    
    if ordering:
        moves = sorted(moves, key=lambda m: value_fn(play_move(board, opponent, m[0], m[1]), color), reverse = False ) #for key: score each move by looking at the board it produce
        #lambda here is for define a function quickly due to sortered() functoin need a function that tells how to rank each item
        
    for m in moves:
        new_board = play_move(board, opponent, m[0], m[1])

        _, value = alphabeta_max_node(value_fn,new_board,color,alpha,beta,limit-1,caching,ordering)

        if value < best_value:
            best_value = value
            best_move = m
        beta = min(beta, best_value)
        
        if beta <= alpha:
            break
        
    state_cache[key] = (best_move, best_value)
    return best_move, best_value

def alphabeta_max_node(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        alpha: int,
        beta: int,
        limit: int,
        caching: int = 0,
        ordering: int = 0) -> tuple[Optional[tuple[int, int]], int]:
    """
    Return a tuple of the move that yields the *highest* possible utility
    and the *highest* possible utility itself for the given board, color,
    limit, value_fn to determine utility and alpha, beta to prune.
    Optionally use state caching and node ordering.

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param alpha: the alpha parameter, used in pruning
    :param beta: the beta parameter, used in pruning
    :param limit: the depth limit of the alpha-beta search
    :param caching: whether to use state caching
                    if 1, use state caching
                    if 0, do not use state caching
    :param ordering: whether to order moves during move selection

    :return: a tuple (None|(i,j), utility) of the next move to be
             taken, and the utility value associated with it
    """
    # TODO: Implement
    if limit == 0:
        return None, value_fn(board, color)
    
    key = (board, color, limit)
    #avoid regenerating same board
    if caching and key in state_cache:
        return state_cache[key]
    
    player = color
    moves = get_possible_moves(board, player)
    oponent = 2 if player == 1 else 1
    
    if ordering:
        moves = sorted(moves, key=lambda m: value_fn(play_move(board, player, m[0], m[1]), color), reverse = True ) 
        
    #case: player terminates, need check if oponent also terminates
    if not moves:
        oponent_move = get_possible_moves(board, oponent)
        if oponent_move:
            return alphabeta_min_node(value_fn,board,color,alpha,beta,limit,caching,ordering)
        else:
            return None, value_fn(board, color)
    
    best_value = float('-inf')
    best_move = None  
    for m in moves:
        new_board = play_move(board, player, m[0], m[1])
        _, value = alphabeta_min_node(value_fn,new_board,color,alpha,beta,limit-1,caching,ordering)# since we only care about the value
        
        if value > best_value:
            best_value = value
            best_move = m

        alpha = max(alpha, best_value)
        
        #prune other braches
        if alpha >= beta:
            break
    
    state_cache[key] = (best_move, best_value)
    
    return best_move, best_value

def select_move_alphabeta(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        limit: int = -1,
        caching: int = 0,
        ordering: int = 0) -> Optional[tuple[int, int]]:
    """
    Return the next move determined by alpha-beta pruning in a game of Othello
    defined by the given board, player color, depth limit, and use of caching
    and node ordering. Use value_fn to determine utility values in subroutines.

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param limit: the depth limit of the alpha-beta search
    :param caching: whether to use state caching
                    if 1, use state caching
                    if 0, do not use state caching
    :param ordering: whether to order moves during move selection

    :return: a tuple (i, j) of the next move to be taken, or None
    """
    # TODO: Implement
    alpha = float('-inf')
    beta = float('inf')
    
    move, _ = alphabeta_max_node(value_fn,board,color,alpha,beta,limit,caching,ordering)
    
    return move


###############################################################################
############################# MINIMAX FUNCTIONS ###############################
###############################################################################
def minimax_min_node(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        limit: int,
        caching: int = 0) -> tuple[Optional[tuple[int, int]], int]:
    """
    Return a tuple of the move that yields the lowest possible utility
    and the lowest possible utility itself for the given board, color,
    limit, using value_fn to determine utility. Optionally use state caching
    and node ordering.

    The algorithm is outlined as follows:
        1. Get all allowed moves
        2. Check if we are at a terminal state
        3. If not, minimize over the set of max utility values for each possible move

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param limit: the depth limit of the Minimax search
    :param caching: whether to use state caching in Minimax
                    if 1, use state caching
                    if 0, do not use state caching

    :return: a tuple (None|(i,j), utility) of the next move to be
             taken, and the utility value associated with it
    """
    # TODO: Implement
    if limit == 0:
        return None, value_fn(board, color)
    
    key = (board, color, limit)
    #avoid regenerating same board
    if caching and key in state_cache:
        return state_cache[key]
    
    opponent = 2 if color == 1 else 1

    moves = get_possible_moves(board, opponent)

    # Terminal state
    if not moves:
        return None, value_fn(board, color)

    best_value = float('inf')
    best_move = None

    for m in moves:
        new_board = play_move(board, opponent, m[0], m[1])

        _, value = minimax_max_node(
            value_fn,
            new_board,
            color,
            limit-1,
            caching
        )

        if value < best_value:
            best_value = value
            best_move = m

    state_cache[key] = (best_move, best_value)
    
    return best_move, best_value

def minimax_max_node(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        limit: int,
        caching: int = 0) -> tuple[Optional[tuple[int, int]], int]:
    """
    Return a tuple of the move that yields the highest possible utility
    and the highest possible utility itself for the given board, color,
    limit, using value_fn to determine utility. Optionally use state caching
    and node ordering.

    The algorithm is outlined as follows:
        1. Get all allowed moves
        2. Check if we are at a terminal state
        3. If not, maximize over the set of min utility values for each possible move

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param limit: the depth limit of the Minimax search
    :param caching: whether to use state caching in Minimax
                    if 1, use state caching
                    if 0, do not use state caching

    :return: a tuple (None|(i,j), utility) of the next move to be
             taken, and the utility value associated with it
    """
    # TODO: Implement
    if limit == 0:
        return None, value_fn(board, color)
    
    key = (board, color, limit)
    #avoid regenerating same board
    if caching and key in state_cache:
        return state_cache[key]
    
    
    player = color
    moves = get_possible_moves(board, player)

    # Terminal state
    if not moves:
        #check if oponent has legal move
        opponent = 2 if color == 1 else 1
        opponent_moves = get_possible_moves(board, opponent)
        if not opponent_moves:
        # true terminal (game over)
            return None, value_fn(board, color)
        else:
        # skip turn → go to MIN node
            return minimax_min_node(value_fn, board, color, limit, caching)

    best_value = float('-inf')
    best_move = None

    #try each positons on board
    for m in moves:
        new_board = play_move(board, player, m[0], m[1])

        #since player is MAX, next step(successor) visited should be MIN
        _, value = minimax_min_node(
            value_fn,
            new_board,
            color,
            limit-1,
            caching
        )

        if value > best_value:
            best_value = value
            best_move = m

    state_cache[key] = (best_move, best_value)
    
    return best_move, best_value

def select_move_minimax(
        value_fn: Callable,
        board: tuple[tuple[int, ...], ...],
        color: int,
        limit: int,
        caching: int = 0) -> Optional[tuple[int, int]]:
    """
    Return the next move determined by Minimax in a game of Othello
    defined by the given board, player color, depth limit, and use of caching.
    Uses value_fn to determine utility values in subroutines.

    :param value_fn: function used to determine utility values
    :param board: the current state of the Othello game
    :param color: the color of the current player (1 for dark, 2 for light)
    :param limit: the depth limit of the Minimax search
    :param caching: whether to use state caching
                    if 1, use state caching
                    if 0, do not use state caching

    :return: a tuple (i, j) of the next move to be taken, or None
    """
    # TODO: Implement
    move, _ = minimax_max_node(value_fn,
        board,
        color,
        limit,
        caching
    )
    return move

###############################################################################
############################### ENTRY-POINT ###################################
###############################################################################
def run_ai():
    """
    Communicate with the game manager to simulate a player in a game
    of Othello. Accepts input from stdin to determine:
        * color    - 1 for dark, 2 for light
        * limit    - the depth limit
        * minimax  - 1 to run minimax, otherwise run alpha-beta
        * caching  - 1 to run with caching, otherwise run without it
        * ordering - 1 to run alpha-beta with node ordering,
                     otherwise run without it.

    Use `compute_utility` as the value function by default.
    """
    print("Othello AI")  # First line is the name of this AI
    color, limit, minimax, caching, ordering = map(int, input().split(","))

    eprint("Running MINIMAX") if minimax else eprint("Running ALPHA-BETA")
    eprint("State Caching is ON") if caching else eprint("State Caching is OFF")
    eprint("Node Ordering is ON") if ordering else eprint("Node Ordering is OFF")
    eprint("Depth Limit is ", limit) if limit >= 0 else eprint("Depth Limit is OFF")

    while True:
        # Read the current state of the game as yielded by the game manager.
        # Consists of a string of the form:
        #
        #       (SCORE|FINAL) \d+ \d+    , e.g. SCORE 9 7
        #
        # The first string is the state of the game:
        #   * SCORE indicates that the game is still active.
        #   * FINAL indicates that the game is over.
        #
        # The first digit is the score for player 1 (the dark player.)
        #
        # The second digit is the score for player 2 (the light player.)
        status, _, _ = input().strip().split()

        if status == "FINAL":
            break
        else:
            # Read the current board represented as a tuple of tuples, where
            # nested tuples represent rows of the board. For example:
            #
            #   ((0, 0, 0, 0),
            #    (0, 2, 1, 0),
            #    (0, 1, 2, 0),
            #    (0, 0, 0, 0))
            #
            # where
            #
            #   * 0 - an empty square on the board
            #   * 1 - a piece played by player 1, or the dark player.
            #   * 2 - a piece played by player 2, or the light player.
            board = eval(input())

            if (minimax == 1):
                i, j = select_move_minimax(
                    compute_utility,
                    board,
                    color,
                    limit,
                    caching
                )
            else:
                i, j = select_move_alphabeta(
                    compute_utility,
                    board,
                    color,
                    limit,
                    caching,
                    ordering
                )

            print("{} {}".format(i, j))


if __name__ == "__main__":
    run_ai()
