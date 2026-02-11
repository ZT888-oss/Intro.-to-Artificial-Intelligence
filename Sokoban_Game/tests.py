import time
from typing import List, Callable

from solution import (
    iterative_astar,
    iterative_gbfs,
    heur_manhattan_distance,
    heur_alternate,
    fval_function,
    weighted_astar,
)
from src import (
    sokoban_goal_state,
    SokobanState,
    SOKOBAN_PROBLEMS as PROBLEMS,
    SearchNode,
    SearchEngine,
)
from test_utils import (
    TestOutput,
    compare_to_benchmark
)

MAX_SCORES = {
    "test_manhattan_distance": 22,
    "test_alternate_heuristic": 25,
    "test_fval_function": 3,
    "test_iterative_gbfs": 25,
    "test_iterative_astar": 25,
    "test_weighted_astar": 10,
}


def test_timekeeping(
        search_fn: Callable,
        name: str,
        start_state,
        heur_fn: Callable = None,
        weight: float = None,
        timebound: float = 7.0,
) -> TestOutput:
    """Generic time-keeping test for search functions."""
    errors = ""
    output = ""
    score = 0

    try:
        heur_fn(start_state)
    except Exception as ex:
        errors = f"Exception encountered in heuristic: {ex}"
        return TestOutput(name=name, score=0, max_score=1, errors=errors)

    t0 = time.perf_counter()
    if weight is not None:
        search_fn(start_state, heur_fn=heur_fn, weight=weight, timebound=timebound)
    else:
        search_fn(start_state, heur_fn=heur_fn, timebound=timebound)
    elapsed = time.perf_counter() - t0

    if elapsed <= timebound + 0.1:
        score = 1
        output = f"Completed within timebound. Elapsed: {elapsed:.4f}s."
    else:
        errors = f"Time exceeded by {elapsed - timebound:.4f}s. Limit was {timebound:.4f}s."

    return TestOutput(name=name, score=score, max_score=1, output=output, errors=errors)


def test_time_astar_fun() -> TestOutput:
    """Tests if iterative_astar respects the timebound on a difficult problem."""
    start = PROBLEMS[19]
    result = test_timekeeping(
        iterative_astar, "iterative_astar", start,
        heur_fn=heur_alternate, weight=2
    )
    result.description = "Tests if iterative_astar respects the timebound on a difficult problem."
    return result


def test_time_gbfs_fun() -> TestOutput:
    """Tests if iterative_gbfs respects the timebound on a difficult problem."""
    start = PROBLEMS[19]
    result = test_timekeeping(
        iterative_gbfs, "iterative_gbfs", start,
        heur_fn=heur_alternate
    )
    result.description = "Tests if iterative_gbfs respects the timebound on a difficult problem."
    return result


def test_manhattan_fun() -> TestOutput:
    """Tests the Manhattan distance heuristic on all problems."""
    correct_distances = [4, 8, 8, 3, 3,
                         11, 7, 11, 10, 12,
                         12, 13, 10, 13, 10,
                         35, 28, 41, 43, 36,
                         2, 2]

    sub_tests: List[TestOutput] = []
    passed_count = 0

    for idx, state in enumerate(PROBLEMS):
        sub_test_name = f"Problem {idx}"
        score = 0
        output = ""
        errors = ""
        try:
            val = heur_manhattan_distance(state)
            output = f"Got {val}, expected {correct_distances[idx]}"
            if val == correct_distances[idx]:
                passed_count += 1
                score = 1
            else:
                score = 0
                errors = "Incorrect distance calculated."
        except Exception as ex:
            score = 0
            errors = f"Exception encountered: {ex}"

        sub_tests.append(TestOutput(
            name=sub_test_name, score=score, max_score=1,
            output=output, errors=errors
        ))

    summary_output = f"Passed {passed_count}/{len(PROBLEMS)} problems."

    return TestOutput(
        name="test_manhattan_distance",
        score=passed_count,
        max_score=MAX_SCORES["test_manhattan_distance"],
        description="Tests the Manhattan distance heuristic on all problems.",
        output=summary_output,
        sub_tests=sub_tests
    )


def test_alternate_fun() -> TestOutput:
    """Tests the alternate heuristic by solving problems within a timebound."""
    sub_tests: List[TestOutput] = []
    timebound = 2.0

    manhattan_scores = [29, 24, 23, 24, 12, -99,
                        -99, 41, 20, -99, -99, -99,
                        -99, -99, -99, -99, -99, -99,
                        -99, -99, 30, 21]
    benchmark_scores = [-99, 24, 23, 20, 12, -99,
                        -99, 41, 20, -99, 73, 52,
                        64, 39, 40, 160, 139, -99,
                        -99, 207, 30, 19]

    manhattan_solved = sum(i != -99 for i in manhattan_scores)
    benchmark_solved = sum(i != -99 for i in benchmark_scores)

    for idx, state in enumerate(PROBLEMS):
        sub_test_name = f"Problem {idx}"
        score = 0
        output = ""
        errors = ""

        try:
            se = SearchEngine("best_first", "full")
            se.init_search(
                state,
                goal_fn=sokoban_goal_state,
                heur_fn=heur_alternate)
            final, stats = se.search(timebound)

            if final:
                score = 1
                output = f"Solved with cost {final.gval}."
            else:
                score = 0
                errors = "Not solved within 2.0s."
        except Exception as ex:
            score = 0
            errors = f"Exception: {ex}"

        sub_tests.append(TestOutput(
            name=sub_test_name, score=score, max_score=1,
            output=output, errors=errors
        ))

    passed_count = sum(sub_test.score for sub_test in sub_tests)
    score = compare_to_benchmark(passed_count, manhattan_solved, benchmark_solved)
    output = (
        f"You solved {passed_count}/{len(PROBLEMS)} problems in less than {timebound}s.\n"
        f"Manhattan distance solved {manhattan_solved}/{len(PROBLEMS)}.\n"
        f"Our benchmark solved {benchmark_solved}/{len(PROBLEMS)}."
    )

    return TestOutput(
        name="test_alternate_heuristic",
        score=score,
        max_score=MAX_SCORES["test_alternate_heuristic"],
        description="Tests the alternate heuristic by solving problems within a timebound.",
        output=output,
        sub_tests=sub_tests
    )


def test_fval_function_fun() -> TestOutput:
    """Tests the fval_function with different weights."""
    state = SokobanState(
        "START", 6,
        None,
        None, None,
        None, None,
        None, None
    )
    correct = [6, 11, 16]
    weights = [0.01, 0.5, 1.0]
    sub_tests: List[TestOutput] = []
    passed_count = 0

    for idx, w in enumerate(weights):
        sub_test_name = f"Weight {w}"
        score = 0
        output = ""
        errors = ""

        try:
            wrapped_fval_function = (lambda sN: fval_function(sN, w))
            node = SearchNode(state, hval=10, fval_function=wrapped_fval_function)
            val = round(fval_function(node, w), 0)
            output = f"Got {val}, expected {correct[idx]}"
            if val == correct[idx]:
                passed_count += 1
                score = 1
            else:
                score = 0
                errors = "Incorrect f-value."
        except Exception as ex:
            score = 0
            errors = f"Exception: {ex}"

        sub_tests.append(TestOutput(
            name=sub_test_name, score=score, max_score=1,
            output=output, errors=errors
        ))

    return TestOutput(
        name="test_fval_function",
        score=passed_count,
        max_score=MAX_SCORES["test_fval_function"],
        description="Tests the fval_function with different weights.",
        sub_tests=sub_tests
    )


def test_iterative_gbfs_fun() -> TestOutput:
    """Tests iterative_gbfs on all problems, checking for solutions and path cost."""

    manhattan_scores = [20, 19, 21, 20, 8, -99,
                        -99, 41, 15, -99, -99, -99,
                        -99, -99, -99, -99, -99, -99,
                        -99, -99, 30, 19]
    benchmark_scores = [-99, 19, 21, 20, 9, -99,
                        -99, 41, 15, -99, 73, 49,
                        62, 39, 38, 160, 139, -99,
                        -99, 207, 30, 19]

    manhattan_solved = sum(i != -99 for i in manhattan_scores)
    benchmark_solved = sum(i != -99 for i in benchmark_scores)

    sub_tests: List[TestOutput] = []
    exceeded_count = 0
    timebound = 2.0

    for idx, state in enumerate(PROBLEMS):
        sub_test_name = f"Problem {idx}"
        score = 0
        output = ""
        errors = ""

        try:
            final, stats = iterative_gbfs(
                state,
                heur_fn=heur_alternate,
                timebound=timebound
            )
            if final:
                score = 1
                cost = final.gval
                bm = benchmark_scores[idx]
                output = f"Solved with cost {cost}. Benchmark: {'N/A' if bm == -99 else bm}"
                if bm == -99 or cost <= bm:
                    exceeded_count += 1
                else:
                    output = f"Path cost {cost} exceeds benchmark {bm}."
            else:
                errors = f"Not solved within {timebound}s."
        except Exception as ex:
            errors = f"Exception: {ex}"

        sub_tests.append(TestOutput(
            name=sub_test_name,
            score=score,
            max_score=1,
            output=output,
            errors=errors
        ))

    passed_count = sum(sub_test.score for sub_test in sub_tests)
    score = compare_to_benchmark(passed_count, manhattan_solved, benchmark_solved)
    output = (
        f"You solved {passed_count}/{len(PROBLEMS)} problems within the time limit.\n"
        f"Manhattan solved {manhattan_solved} and a better heuristic solved {benchmark_solved}."
    )

    return TestOutput(
        name="test_iterative_gbfs",
        score=score,
        max_score=MAX_SCORES["test_iterative_gbfs"],
        description="Tests iterative_gbfs on all problems for correctness and path cost.",
        output=output,
        sub_tests=sub_tests
    )


def test_iterative_astar_fun() -> TestOutput:
    """Tests iterative_astar on all problems, checking for solutions and path cost."""
    manhattan_scores = [17, 18, 21, 10, 8, -99,
                        -99, 41, 14, -99, -99, -99,
                        -99, -99, -99, -99, -99, -99,
                        -99, -99, 30, 19]
    benchmark_scores = [-99, 16, 21, 10, 8, -99,
                        -99, 41, 14, -99, 36, 30,
                        28, 27, 27, -99, -99, -99,
                        -99, -99, 30, 19]

    manhattan_solved = sum(i != -99 for i in manhattan_scores)
    benchmark_solved = sum(i != -99 for i in benchmark_scores)

    sub_tests: List[TestOutput] = []
    exceeded_count = 0
    timebound = 2.0

    for idx, state in enumerate(PROBLEMS):
        sub_test_name = f"Problem {idx}"
        score = 0
        output = ""
        errors = ""

        try:
            final, stats = iterative_astar(
                state,
                heur_fn=heur_alternate,
                weight=10,
                timebound=timebound
            )
            if final:
                score = 1
                cost = final.gval
                bm = benchmark_scores[idx]
                output = f"Solved with cost {cost}. Benchmark: {'N/A' if bm == -99 else bm}"
                if bm == -99 or cost <= bm:
                    exceeded_count += 1
                else:
                    output = f"Path cost {cost} exceeds benchmark {bm}."
            else:
                errors = f"Not solved within {timebound}s."
        except Exception as ex:
            errors = f"Exception: {ex}"

        sub_tests.append(TestOutput(
            name=sub_test_name,
            score=score,
            max_score=1,
            output=output,
            errors=errors
        ))

    passed_count = sum(sub_test.score for sub_test in sub_tests)
    score = compare_to_benchmark(passed_count, manhattan_solved, benchmark_solved)
    output = (
        f"You solved {passed_count}/{len(PROBLEMS)} problems within the time limit.\n"
        f"Manhattan solved {manhattan_solved} and a better heuristic solved {benchmark_solved}."
    )

    return TestOutput(
        name="test_iterative_astar",
        score=score,
        max_score=MAX_SCORES["test_iterative_astar"],
        description="Tests iterative_astar on all problems for correctness and path cost.",
        output=output,
        sub_tests=sub_tests
    )


def test_weighted_astar_fun() -> TestOutput:
    """Tests weighted_astar for state expansion and solution consistency."""
    weights = [10, 5, 2, 1]
    problems_to_test = 5
    sub_tests: List[TestOutput] = []

    for idx in range(problems_to_test):
        state = PROBLEMS[idx]
        counts: List[int] = []
        costs: List[int] = []

        output = ""
        errors = ""

        for w in weights:
            try:
                final, stats = weighted_astar(
                    state, heur_fn=heur_manhattan_distance, weight=w, timebound=5.0
                )
                if final:
                    output = f"Weight {w}: Solved (cost: {final.gval}," \
                             f" expanded: {stats.states_expanded if stats else 'N/A'})\n" \
                             + output
                    counts.append(stats.states_expanded if stats else -1)
                    costs.append(final.gval)
                else:
                    output = f"Weight {w}: Not solved\n" + output
                    counts.append(-99)
                    costs.append(-99)
            except Exception as ex:
                errors = f"Weight {w}: Exception: {ex}\n" + output
                counts.append(-99)
                costs.append(-99)

        # State expansion consistency check
        exp_check_name = f"Problem {idx} State Expansion Monotonicity"
        comparisons_made = [counts[i] <= counts[i + 1] for i in range(len(counts) - 1) if
                            counts[i] != -99 and counts[i + 1] != -99]
        if comparisons_made and all(comparisons_made):
            score = 1
        else:
            score = 0

        sub_tests.append(TestOutput(
            name=exp_check_name, score=score, max_score=1,
            output=output, errors=errors
        ))

        # Solution existence consistency check
        sol_check_name = f"Problem {idx} Solution Existence Consistency"
        sol_consistent = all(
            not (costs[i] == -99 and costs[i + 1] != -99) for i in range(len(costs) - 1)
        )

        if len(costs) >= 2 and not all(c == -99 for c in costs) and sol_consistent:
            score = 1
        else:
            score = 0

        sub_tests.append(TestOutput(
            name=sol_check_name, score=score, max_score=1,
            output=output, errors=errors
        ))

    return TestOutput(
        name="test_weighted_astar",
        score=sum(sub_test.score for sub_test in sub_tests),
        max_score=MAX_SCORES["test_weighted_astar"],
        description="Tests weighted_astar for state expansion and solution consistency.",
        sub_tests=sub_tests
    )


# List of tests
SOKOBAN_TESTS = [
    (
        test_manhattan_fun,
        (),
        "test_manhattan_distance",
        MAX_SCORES["test_manhattan_distance"]
    ),
    (
        test_alternate_fun,
        (),
        "test_alternate_heuristic",
        MAX_SCORES["test_alternate_heuristic"]
    ),
    (
        test_fval_function_fun,
        (),
        "test_fval_function",
        MAX_SCORES["test_fval_function"]
    ),
    (
        test_iterative_gbfs_fun,
        (),
        "test_iterative_gbfs",
        MAX_SCORES["test_iterative_gbfs"]
    ),
    (
        test_time_gbfs_fun,
        (),
        "test_time_gbfs",
        1
    ),
    (
        test_iterative_astar_fun,
        (),
        "test_iterative_astar",
        MAX_SCORES["test_iterative_astar"]
    ),
    (
        test_weighted_astar_fun,
        (),
        "test_weighted_astar",
        MAX_SCORES["test_weighted_astar"]
    ),
    (
        test_time_astar_fun,
        (),
        "test_time_astar",
        1
    )
]
