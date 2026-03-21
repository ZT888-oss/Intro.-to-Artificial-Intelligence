import os

from test_utils import TestOutput

try:
    import agent
except ImportError:
    pass



# boards of size 4
SMALL_BOARDS = [((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 0, 0, 0)),
                ((0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 1), (0, 0, 0, 2)),
                ((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 1, 1, 0)),
                ((0, 1, 0, 0), (0, 2, 2, 0), (0, 1, 2, 1), (0, 0, 2, 2)),
                ((1, 0, 0, 2), (1, 1, 2, 0), (1, 1, 1, 1), (1, 2, 2, 2)),
                ((0, 1, 0, 0), (0, 1, 1, 0), (2, 2, 2, 1), (0, 0, 0, 2))]

# boards of size 6
BIG_BOARDS = [((0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0), (0, 1, 1, 2, 2, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0),
               (0, 0, 0, 0, 0, 0)),
              ((0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0),
               (0, 0, 0, 0, 0, 0)),
              ((0, 0, 0, 0, 1, 0), (0, 0, 1, 1, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 2, 0, 1, 2, 0),
               (0, 0, 2, 2, 1, 0)),
              ((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 2, 2, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0),
               (0, 0, 0, 0, 0, 0)),
              ((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 1, 1, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0),
               (0, 0, 0, 0, 0, 0))]


#######################################
# TEST FUNCTIONS
#######################################
def compute_utility_test(compute_utility, test_name) -> TestOutput:
    """Tests the compute_utility function on small boards."""
    correctvalues = [3, 3, 5, -2, 3, 0]
    score = 0
    output = ""
    errors = ""

    for i, board in enumerate(SMALL_BOARDS):
        try:
            value1 = compute_utility(board, 1)
            value2 = compute_utility(board, 2)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        if value1 == correctvalues[i] and value2 == -correctvalues[i]:
            score += 1
        else:
            errors += (f"Board {i}: expected ({correctvalues[i]}, {-correctvalues[i]}), "
                        f"got ({value1}, {value2})\n")
    
    max_score = len(correctvalues)
    if score == max_score:
        output = f"All {max_score} utility tests passed"
    else:
        output = f"Passed {score}/{max_score} utility tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=len(correctvalues),
        description="Tests the compute_utility function on small boards.",
        output=output,
        errors=errors
    )


def select_move_minimax_test(value_fn, select_move_minimax, test_name) -> TestOutput:
    """Tests the select_move_minimax function on small boards."""
    correctmoves_1 = [(0, 0), (2, 3), (0, 0), (3, 0), (3, 1), (0, 3)]
    correctmoves_2 = [(3, 3), (0, 0), (3, 3), (0, 2), (3, 1), (0, 0)]
    score = 0
    output = ""
    errors = ""

    for i, board in enumerate(SMALL_BOARDS):
        try:
            move1 = select_move_minimax(value_fn, board, 1, 6)
            move2 = select_move_minimax(value_fn, board, 2, 6)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        if move1 == correctmoves_1[i] and move2 == correctmoves_2[i]:
            score += 1
        else:
            errors += (f"Board {i}: expected moves {correctmoves_1[i]}, {correctmoves_2[i]}; "
                        f"got {move1}, {move2}\n")
    
    max_score = len(correctmoves_1)
    if score == max_score:
        output = f"All {max_score} minimax move tests passed"
    else:
        output = f"Passed {score}/{max_score} minimax move tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=len(correctmoves_1),
        description="Tests the select_move_minimax function on small boards.",
        output=output,
        errors=errors
    )


def select_move_alphabeta_test(value_fn, select_move_alphabeta, test_name) -> TestOutput:
    """Tests the select_move_alphabeta function on small boards."""
    correctmoves_1 = [(0, 0), (2, 3), (0, 0), (3, 0), (3, 1), (0, 3)]
    correctmoves_2 = [(3, 3), (0, 0), (3, 3), (0, 2), (3, 1), (0, 0)]
    score = 0
    output = ""
    errors = ""
    
    for i, board in enumerate(SMALL_BOARDS):
        try:
            move1 = select_move_alphabeta(value_fn, board, 1, 6)
            move2 = select_move_alphabeta(value_fn, board, 2, 6)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        if move1 == correctmoves_1[i] and move2 == correctmoves_2[i]:
            score += 1
        else:
            errors += (f"Board {i}: expected moves {correctmoves_1[i]}, {correctmoves_2[i]}; "
                        f"got {move1}, {move2}\n")
    
    max_score = len(correctmoves_1)
    if score == max_score:
        output = f"All {max_score} alphabeta move tests passed"
    else:
        output = f"Passed {score}/{max_score} alphabeta move tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=len(correctmoves_1),
        description="Tests the select_move_alphabeta function on small boards.",
        output=output,
        errors=errors
    )

def select_move_equal_test(value_fn, funcs, test_name) -> TestOutput:
    """Tests that minimax and alphabeta return the same moves."""
    # funcs is a tuple: (select_move_minimax, select_move_alphabeta)
    select_move_minimax, select_move_alphabeta = funcs
    correctmoves_1 = [(0, 0), (2, 3), (0, 0), (3, 0), (3, 1)]
    correctmoves_2 = [(3, 3), (0, 0), (3, 3), (0, 2), (3, 1)]
    score = 0
    output = ""
    errors = ""
    
    for i in range(len(correctmoves_1)):
        board = SMALL_BOARDS[i]
        try:
            move1_minimax = select_move_minimax(value_fn, board, 1, 6)
            move1_alphabeta = select_move_alphabeta(value_fn, board, 1, 6)
            move2_minimax = select_move_minimax(value_fn, board, 2, 6)
            move2_alphabeta = select_move_alphabeta(value_fn, board, 2, 6)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        if move1_minimax == move1_alphabeta == correctmoves_1[i] and move2_minimax == move2_alphabeta == correctmoves_2[i]:
            score += 1
        else:
            errors += (f"Board {i}: minimax moves ({move1_minimax}, {move2_minimax}) != "
                        f"alphabeta moves ({move1_alphabeta}, {move2_alphabeta})\n")
    
    max_score = len(correctmoves_1)
    if score == max_score:
        output = f"All {max_score} equality tests passed"
    else:
        output = f"Passed {score}/{max_score} equality tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests that minimax and alphabeta return the same moves.",
        output=output,
        errors=errors
    )


def caching_test(value_fn, select_move_alphabeta, boards, agent_module, test_name,
                 score_timing=True, time_threshold=0.15) -> TestOutput:
    """Tests that alphabeta uses caching to improve performance."""
    move_score = 0
    time_score = 0
    output = ""
    errors = ""

    for i, board in enumerate(boards):
        try:
            # Clear cache before each test
            if hasattr(agent_module, 'cache'):
                agent_module.cache.clear()

            # Call without caching: correctness reference + time baseline
            start_time = os.times()[0]
            move_no_cache = select_move_alphabeta(value_fn, board, 1, 6)
            time_no_cache = os.times()[0] - start_time

            # First call with caching: cold cache, warms it (not timed)
            select_move_alphabeta(value_fn, board, 1, 6, 1)

            # Second call with caching: warm cache should be much faster
            start_time = os.times()[0]
            move_warm_cache = select_move_alphabeta(value_fn, board, 1, 6, 1)
            time_warm_cache = os.times()[0] - start_time

            if move_no_cache == move_warm_cache:
                move_score += 1
            if score_timing:
                if time_no_cache - time_warm_cache > time_threshold:
                    time_score += 1
                else:
                    errors += f"Board {i}: caching not effective (time_no_cache: {time_no_cache:.4f}, time_warm_cache: {time_warm_cache:.4f})\n"

        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue

    max_score = len(boards) * (2 if score_timing else 1)
    if move_score == len(boards):
        output = f"All {len(boards)} move caching tests passed"
    else:
        output = f"Passed {move_score}/{len(boards)} move caching tests"
    if score_timing:
        if time_score == len(boards):
            output += f"\nAll {len(boards)} time caching tests passed"
        else:
            output += f"\nPassed {time_score}/{len(boards)} time caching tests"

    return TestOutput(
        name=test_name,
        score=move_score + (time_score if score_timing else 0),
        max_score=max_score,
        description="Tests that alphabeta uses caching to improve performance.",
        output=output,
        errors=errors
    )


def caching_big_test(value_fn, select_move_alphabeta, agent_module, test_name) -> TestOutput:
    """Tests caching on big boards."""
    return caching_test(value_fn, select_move_alphabeta, BIG_BOARDS, agent_module, test_name, time_threshold=0.035)


def caching_small_test(value_fn, select_move_alphabeta, agent_module, test_name) -> TestOutput:
    """Tests caching on small boards."""
    return caching_test(value_fn, select_move_alphabeta, SMALL_BOARDS, agent_module, test_name, score_timing=False)


def ordering_test(value_fn, select_move_alphabeta, boards, expected_move_change,
                  score_timing, test_name, time_threshold=0.15) -> TestOutput:
    """Tests that move ordering improves alphabeta performance.

    expected_move_change: list of bools, one per board. True means ordering is
    expected to select a different (but equally optimal) move due to tie-breaking.
    score_timing: if True, speed improvement is included in the score. Set to
    False for boards where sort overhead can outweigh pruning gains.
    """
    move_score = 0
    time_score = 0
    output = ""
    errors = ""

    for i, board in enumerate(boards):
        try:
            # Test without ordering
            start_time = os.times()[0]
            move_no_ordering = select_move_alphabeta(value_fn, board, 1, 7, 0, 0)
            time_no_ordering = os.times()[0] - start_time

            # Test with ordering
            start_time = os.times()[0]
            move_ordering = select_move_alphabeta(value_fn, board, 1, 7, 0, 1)
            time_ordering = os.times()[0] - start_time

            if score_timing:
                if time_no_ordering - time_ordering > time_threshold:
                    time_score += 1
                else:
                    errors += f"Board {i}: ordering not effective (time_no_ordering: {time_no_ordering:.4f}, time_ordering: {time_ordering:.4f})\n"
            else:
                output += f"Board {i}: time without ordering: {time_no_ordering:.4f}, with ordering: {time_ordering:.4f}\n"

            if (move_no_ordering != move_ordering) == expected_move_change[i]:
                move_score += 1
            else:
                errors += f"Board {i}: expected move change {expected_move_change[i]}, got {move_no_ordering != move_ordering}\n"

        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue

    if score_timing:
        max_score = len(boards) * 2
        score = move_score + time_score
        if time_score == len(boards):
            output += f"All {len(boards)} time ordering tests passed\n"
        else:
            output += f"Passed {time_score}/{len(boards)} time ordering tests\n"
    else:
        max_score = len(boards)
        score = move_score

    if move_score == len(boards):
        output += f"All {len(boards)} move ordering tests passed"
    else:
        output += f"Passed {move_score}/{len(boards)} move ordering tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests that move ordering improves alphabeta performance.",
        output=output,
        errors=errors
    )


def ordering_small_test(value_fn, select_move_alphabeta, test_name) -> TestOutput:
    """Tests ordering on small boards."""
    return ordering_test(
        value_fn, select_move_alphabeta, SMALL_BOARDS,
        expected_move_change=[False, False, False, False, False, False],
        score_timing=False,
        test_name=test_name
    )


def ordering_big_test(value_fn, select_move_alphabeta, test_name) -> TestOutput:
    """Tests ordering on big boards."""
    return ordering_test(
        value_fn, select_move_alphabeta, BIG_BOARDS,
        expected_move_change=[False, True, False, True, True],
        score_timing=True,
        time_threshold=0.005,
        test_name=test_name
    )

def alphabeta_min_node_1_test(value_fn, alpha_beta_min_node_fn, test_name) -> TestOutput:
    """Tests alphabeta_min_node function on small boards."""
    answers = [((2, 4), -10), ((1, 1), -4), ((3, 0), -6), ((0, 1), -8), ((5, 2), -6)]
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i, board in enumerate(BIG_BOARDS[:len(answers)]):
        try:
            move, value = alpha_beta_min_node_fn(value_fn, board, 1, float("-Inf"), float("Inf"), 1, 0, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} alphabeta min node tests passed"
    else:
        output = f"Passed {score}/{max_score} alphabeta min node tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests alphabeta_min_node function on big boards.",
        output=output,
        errors=errors
    )


def alphabeta_max_node_1_test(value_fn, alpha_beta_max_node_fn, test_name) -> TestOutput:
    """Tests alphabeta_max_node function on small boards."""
    # Only testing selected boards (indices 1, 2, and 4)
    answers = {1: ((5, 5), 8), 2: ((1, 5), 12), 4: ((3, 4), 4)}
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i in sorted(answers.keys()):
        board = BIG_BOARDS[i]
        try:
            move, value = alpha_beta_max_node_fn(value_fn, board, 1, float("-Inf"), float("Inf"), 1, 0, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} alphabeta max node tests passed"
    else:
        output = f"Passed {score}/{max_score} alphabeta max node tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests alphabeta_max_node function on big boards.",
        output=output,
        errors=errors
    )


def minimax_min_node_1_test(value_fn, min_node_fn, test_name) -> TestOutput:
    """Tests minimax_min_node function on small boards."""
    answers = [((2, 4), -10), ((1, 1), -4), ((3, 0), -6), ((0, 1), -8), ((5, 2), -6)]
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i, board in enumerate(BIG_BOARDS[:len(answers)]):
        try:
            move, value = min_node_fn(value_fn, board, 1, 1, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} minimax min node tests passed"
    else:
        output = f"Passed {score}/{max_score} minimax min node tests"


    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests minimax_min_node function on big boards.",
        output=output,
        errors=errors
    )


def minimax_max_node_1_test(value_fn, max_node_fn, test_name) -> TestOutput:
    """Tests minimax_max_node function on small boards."""
    # Only testing selected boards (indices 1, 2, and 4)
    answers = {1: ((5, 5), 8), 2: ((1, 5), 12), 4: ((3, 4), 4)}
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i in sorted(answers.keys()):
        board = BIG_BOARDS[i]
        try:
            move, value = max_node_fn(value_fn, board, 1, 1, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} minimax max node tests passed"
    else:
        output = f"Passed {score}/{max_score} minimax max node tests"
            

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests minimax_max_node function on big boards.",
        output=output,
        errors=errors
    )


def alphabeta_min_node_2_test(value_fn, alpha_beta_min_node_fn, test_name) -> TestOutput:
    """Tests alphabeta_min_node function on big boards."""
    answers = [((3, 0), -6), ((5, 5), -8), ((1, 5), -12), ((5, 2), -2), ((3, 4), -4)]
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    

    for i, board in enumerate(BIG_BOARDS[:len(answers)]):
        try:
            move, value = alpha_beta_min_node_fn(value_fn, board, 2, float("-Inf"), float("Inf"), 1, 0, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} alphabeta min node tests passed"
    else:
        output = f"Passed {score}/{max_score} alphabeta min node tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests alphabeta_min_node function on big boards.",
        output=output,
        errors=errors
    )


def alphabeta_max_node_2_test(value_fn, alpha_beta_max_node_fn, test_name) -> TestOutput:
    """Tests alphabeta_max_node function on big boards."""
    # Testing selected boards (indices 1, 2, and 4)
    answers = {1: ((1, 1), 4), 2: ((3, 0), 6), 4: ((5, 2), 6)}
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i in sorted(answers.keys()):
        board = BIG_BOARDS[i]
        try:
            move, value = alpha_beta_max_node_fn(value_fn, board, 2, float("-Inf"), float("Inf"), 1, 0, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} alphabeta max node tests passed"
    else:
        output = f"Passed {score}/{max_score} alphabeta max node tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests alphabeta_max_node function on big boards.",
        output=output,
        errors=errors
    )


def minimax_min_node_2_test(value_fn, min_node_fn, test_name) -> TestOutput:
    """Tests minimax_min_node function on big boards."""
    answers = [((3, 0), -6), ((5, 5), -8), ((1, 5), -12), ((5, 2), -2), ((3, 4), -4)]
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    
    for i, board in enumerate(BIG_BOARDS[:len(answers)]):
        try:
            move, value = min_node_fn(value_fn, board, 2, 1, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} minimax min node tests passed"
    else:
        output = f"Passed {score}/{max_score} minimax min node tests"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests minimax_min_node function on big boards.",
        output=output,
        errors=errors
    )


def minimax_max_node_2_test(value_fn, max_node_fn, test_name) -> TestOutput:
    """Tests minimax_max_node function on big boards."""
    # Testing selected boards (indices 1, 2, and 4)
    answers = {1: ((1, 1), 4), 2: ((3, 0), 6), 4: ((5, 2), 6)}
    correct_moves = 0
    correct_values = 0
    output = ""
    errors = ""
    

    for i in sorted(answers.keys()):
        board = BIG_BOARDS[i]
        try:
            move, value = max_node_fn(value_fn, board, 2, 1, 0)
        except Exception as e:
            errors += f"Board {i}: Exception {e}\n"
            continue
        expected_move, expected_value = answers[i]
        if move == expected_move:
            correct_moves += 1
        else:
            errors += f"Board {i}: expected move {expected_move}, got {move}\n"
        if value == expected_value:
            correct_values += 1
        else:
            errors += f"Board {i}: expected value {expected_value}, got {value}\n"
    
    score = correct_moves + correct_values
    max_score = 2 * len(answers)
    if score == max_score:
        output = f"All {max_score} minimax max node tests passed"
    else:
        output = f"Passed {score}/{max_score} minimax max node tests"


    return TestOutput(
        name=test_name,
        score=score,
        max_score=2 * len(answers),
        description="Tests minimax_max_node function on big boards.",
        output=output,
        errors=errors
    )


othello_tests = [
    (compute_utility_test, (agent.compute_utility,), "Minimax Compute Utility"),
    (select_move_minimax_test, (agent.compute_utility, agent.select_move_minimax), "Minimax Select Move"),
    (minimax_min_node_1_test, (agent.compute_utility, agent.minimax_min_node), "Minimax Min Node Test (Player 1)"),
    (minimax_max_node_1_test, (agent.compute_utility, agent.minimax_max_node), "Minimax Max Node Test (Player 1)"),
    (minimax_min_node_2_test, (agent.compute_utility, agent.minimax_min_node), "Minimax Min Node Test (Player 2)"),
    (minimax_max_node_2_test, (agent.compute_utility, agent.minimax_max_node), "Minimax Max Node Test (Player 2)"),
    (select_move_alphabeta_test, (agent.compute_utility, agent.select_move_alphabeta),  "Alpha-Beta Select Move"),
    (select_move_equal_test, (agent.compute_utility, (agent.select_move_minimax, agent.select_move_alphabeta)), "Alpha-Beta Equal Select Move"),
    (alphabeta_min_node_1_test, (agent.compute_utility, agent.alphabeta_min_node), "Alpha-Beta Min Node Test (Player 1)"),
    (alphabeta_max_node_1_test, (agent.compute_utility, agent.alphabeta_max_node), "Alpha-Beta Max Node Test (Player 1)"),
    (alphabeta_min_node_2_test, (agent.compute_utility, agent.alphabeta_min_node), "Alpha-Beta Min Node Test (Player 2)"),
    (alphabeta_max_node_2_test, (agent.compute_utility, agent.alphabeta_max_node), "Alpha-Beta Max Node Test (Player 2)"),
    (ordering_small_test, (agent.compute_utility, agent.select_move_alphabeta), "Ordering (Small Boards)"),
    (ordering_big_test, (agent.compute_utility, agent.select_move_alphabeta), "Ordering (Big Boards)"),
    (caching_small_test, (agent.compute_utility, agent.select_move_alphabeta, agent), "Caching (Small Boards)"),
    (caching_big_test, (agent.compute_utility, agent.select_move_alphabeta, agent), "Caching (Big Boards)"),
]