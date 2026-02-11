import io
import json
import traceback
import contextlib
import signal
import importlib
import dataclasses
import enum
import math

from typing import List


############################################################
## Timeout utilities
############################################################
class TimeoutException(BaseException):
    """Raised when time is up."""
    def __init__(self, message="Timeout occurred.", partial_score=0):
        super().__init__(message)
        self.partial_score = partial_score

def _timeout_handler(signum, frame):
    raise TimeoutException()

def set_timeout(seconds):
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)

def reset_timeout():
    signal.alarm(0)


############################################################
## Data structures for test results
############################################################
@enum.unique
class TestStatus(enum.Enum):
    PASSED = "PASSED"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"

@dataclasses.dataclass
class TestOutput:
    """A dataclass to record the results of a single test"""
    name: str
    score: int
    max_score: int
    description: str = ""
    output: str = ""
    user_output: str = ""
    errors: str = ""
    sub_tests: List['TestOutput'] = dataclasses.field(default_factory=list)


############################################################
## Test output formatting utilities
############################################################
def check_status(test_output: TestOutput) -> str:
    if test_output.score == test_output.max_score:
        return "[PASSED]"
    elif test_output.score > 0:
        return "[PARTIAL]"
    else:
        return "[FAIL]"

def print_report(results: List[TestOutput], verbose: bool):
    if not verbose:
        for test_result in results:
            print(format_simple_test_result(test_result))
    else:
        print("\n" + "=" * 60)
        print(" " * 18 + "DETAILED TEST RESULTS")
        print("=" * 60)
        for test_result in results:
            print(format_verbose_test_result(test_result))
        print("\n" + "=" * 60)

def format_simple_test_result(test_result: TestOutput) -> str:
    return f"{check_status(test_result)} " \
           f"[{test_result.score}/{test_result.max_score}] " \
           f"{test_result.name} "

def format_verbose_test_result(test_result: TestOutput) -> str:
    """
    Formats a pretty, verbose report for a single test from a TestOutput object.
    """
    report_parts = [
        f"Test: {test_result.name}",
        f"Status: {check_status(test_result)}",
        f"Score: {test_result.score}/{test_result.max_score}",
        "-" * 60,
        ]
    if test_result.description:
        report_parts.extend(["Description:", f"  {test_result.description}", ""])

    if test_result.sub_tests:
        report_parts.append("--- Test Breakdown ---")
        for sub in test_result.sub_tests:
            report_parts.append(f"\n  +-- {sub.name} --")
            report_parts.append(f"  |  Status: {check_status(sub)}")
            report_parts.append(f"  |  Score:  {sub.score}/{sub.max_score}")

            if sub.output:
                indented_output = "\n".join([f"  |    > {line}" for line in sub.output.split('\n') if line])
                report_parts.append(f"  |  Output:\n{indented_output}")

            if sub.errors:
                indented_errors = "\n".join([f"  |    [!] {line}" for line in sub.errors.split('\n') if line])
                report_parts.append(f"  |  Errors:\n{indented_errors}")

            if sub.sub_tests:
                raise NotImplementedError("Nested sub-tests formatting is not implemented.")

        report_parts.append("\n" + ("-" * 26) + "\n")

    if test_result.output:
        report_parts.append("--- Summary Output ---")
        indented_output = "\n".join([f"  {line}" for line in test_result.output.split('\n')])
        report_parts.append(indented_output)
        report_parts.append("----------------------\n")

    if test_result.user_output:
        report_parts.append("--- Your Program's Output ---")
        indented_output = "\n".join([f"  {line}" for line in test_result.user_output.split('\n')])
        report_parts.append(indented_output)
        report_parts.append("---------------------------\n")

    if test_result.errors and test_result.errors != "None":
        report_parts.append("--- Summary Errors ---")
        indented_errors = "\n".join([f"  {line}" for line in test_result.errors.split('\n')])
        report_parts.append(indented_errors)
        report_parts.append("--------------------\n")

    full_report = "\n".join(report_parts)
    return f"{'=' * 60}\n{full_report.strip()}\n{'=' * 60}"


############################################################
## Test running utilities
############################################################
def compare_to_benchmark(
        num_solved: int,
        manhattan_benchmark_solved: int,
        solution_benchmark_solved: int,
        apply_deduction: bool = False):
    """
    Compare the number of problems solved to the benchmark scores.
    """
    score = 0
    # 5 points for solving at least 2 problems
    if num_solved > 0 and num_solved <= 2:
        score = 5
    # 5 - 10 points for solving as many as the manhattan benchmark
    elif num_solved >= 3 and num_solved < manhattan_benchmark_solved:
        student_margin = num_solved - 2
        if student_margin > 0:
            score = 5 + math.ceil((student_margin / manhattan_benchmark_solved) * 5)
    # 10 - 20 points for solving more than manhattan benchmark but less
    # than solution benchmark
    elif num_solved >= manhattan_benchmark_solved and num_solved < solution_benchmark_solved:
        margin = solution_benchmark_solved - manhattan_benchmark_solved
        student_margin = num_solved - manhattan_benchmark_solved
        if (student_margin > 0):
            score = 10 + math.ceil((student_margin / margin) * 10)
        else:
            score = 10
    # 20 - 25 points for solving more than solution benchmark
    elif num_solved >= solution_benchmark_solved:
        score = 20
        solved_better = num_solved - solution_benchmark_solved
        if solved_better >= 1 and solved_better < 3:
            score += 3
        elif solved_better >= 3:
            score += 5

    score = min(score, 25)

    if apply_deduction and score > 10:
        score -= 1

    return score

def load_tests_from_module(module_name, test_list_var_name):
    """
    Dynamically loads tests from a specified module and variable.
    """
    try:
        test_module = importlib.import_module(module_name)
        print(f"Successfully loaded test module: {module_name}.py")
    except ImportError:
        print(f"ERROR: Could not import test module: {module_name}.py. Please ensure it exists.")
        return []

    try:
        tests = getattr(test_module, test_list_var_name)
        if not isinstance(tests, list):
            print(f"ERROR: The variable '{test_list_var_name}' in {module_name}.py is not a list.")
            return []
        # Optionally, add more validation for the structure of each test item
        return tests
    except AttributeError:
        print(f"ERROR: Could not find the test list variable '{test_list_var_name}' in {module_name}.py.")
        return []

def _run_test(test_func, timeout=60, test_args=(), test_name="", max_score=1):
    """Helper function to run an individual test and return a TestOutput object."""
    user_output_buffer = io.StringIO()
    user_error_buffer = io.StringIO()
    try:
        set_timeout(timeout)

        with (
            contextlib.redirect_stdout(user_output_buffer),
            contextlib.redirect_stderr(user_error_buffer)
        ):
            result = test_func(*test_args)

        reset_timeout()

        result.name = test_name
        result.user_output = user_output_buffer.getvalue()
        result.errors = user_error_buffer.getvalue()
        return result

    except TimeoutException as ex:
        stderr_output = user_error_buffer.getvalue()
        timeout_msg = f"{test_name} - TIMEOUT ({timeout}s)"
        if stderr_output:
            errors = f"{timeout_msg}\n\nStderr output:\n{stderr_output}"
        else:
            errors = timeout_msg
        return TestOutput(
            name=test_name,
            score=ex.partial_score,
            max_score=max_score,
            description=f"Timed out after {timeout} seconds.",
            errors=errors,
            output=str(ex),
            user_output=user_output_buffer.getvalue()
        )
    except Exception:
        tb = traceback.format_exc()
        stderr_output = user_error_buffer.getvalue()
        runtime_msg = f"{test_name} - RUNTIME ERROR:\n{tb}"
        if stderr_output:
            errors = f"{runtime_msg}\n\nStderr output:\n{stderr_output}"
        else:
            errors = runtime_msg
        return TestOutput(
            name=test_name,
            score=0,
            max_score=max_score,
            description="Could not run the test because it failed due to a runtime error.",
            errors=errors,
            output="",
            user_output=user_output_buffer.getvalue()
        )

def run_all_tests(tests, timeout=60):
    results = []

    overall_score = 0
    overall_max = 0

    for f, args, name, max_score in tests:
        test_result = _run_test(f, timeout, args, name, max_score)

        overall_score += test_result.score
        overall_max += test_result.max_score
        results.append(test_result)

    return results, overall_score, overall_max



def create_markus_test_results(name, output, marks_earned, marks_total, user_output, errors):
    if marks_total <= 0:
        status = 'pass'
    elif marks_earned <= 0:
        status = 'fail'
    elif marks_earned >= marks_total:
        status = 'pass'
    else:
        status = 'partial'

    return {
        "name": name,
        "output": output,
        "marks_earned": marks_earned,
        "marks_total": marks_total,
        "status": status,
        "errors": errors,
        "user_output": user_output
    }


def format_test_results_for_markus(score, max_score, outputs, name, user_output, errors):
    return [json.dumps(
        create_markus_test_results(
            name,
            outputs,
            score,
            max_score,
            user_output,
            errors
        ),
        indent=2
    )]

