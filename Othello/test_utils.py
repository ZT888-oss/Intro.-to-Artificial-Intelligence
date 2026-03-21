import io
import traceback
import contextlib
import signal
import importlib
import dataclasses
from typing import List
import enum


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


def check_status(test_output: TestOutput) -> str:
    """Check the status of a test output"""
    if test_output.score == test_output.max_score:
        return "[PASSED]"
    elif test_output.score > 0:
        return "[PARTIAL]"
    else:
        return "[FAIL]"


class TimeoutException(Exception):
    """Raised when time is up."""
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException("Timeout occurred")


def set_timeout(seconds):
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)


def reset_timeout():
    """Disable alarm."""
    signal.alarm(0)


def contains_list(lst):
    return any(isinstance(e, list) for e in lst)


def sort_innermost_lists(lst):
    """
    Sort the innermost lists in a list-of-lists-of-lists recursively.
    Used for comparing nested lists ignoring order in the innermost layer.
    """
    if not isinstance(lst, list):
        return
    elif contains_list(lst):
        for e in lst:
            sort_innermost_lists(e)
    else:
        lst.sort()


def print_report(results: List[TestOutput], verbose: bool):
    if not verbose:
        for test_result in results:
            print(format_simple_test_result(test_result))
    else:
        print("\n" + "="*60)
        print(" " * 18 + "DETAILED TEST RESULTS")
        print("="*60)
        for test_result in results:
            print(format_verbose_test_result(test_result))
        print("\n" + "="*60)


def format_simple_test_result(test_result: TestOutput) -> str:
    return f"{check_status(test_result)} [{test_result.score}/{test_result.max_score}] {test_result.name} "


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
            report_parts.append(f"  |  Status: {check_status(sub)}  |  Score:  {sub.score}/{sub.max_score}")

            if sub.output:
                indented_output = "\n".join([f"  |    > {line}" for line in sub.output.split('\n')])
                report_parts.append(f"  |  Output:\n{indented_output}")
            
            if sub.errors:
                indented_errors = "\n".join([f"  |    [!] {line}" for line in sub.errors.split('\n')])
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
        report_parts.append("--- Your Program's Print Statements ---")
        indented_output = "\n".join([f"  {line}" for line in test_result.user_output.split('\n')])
        report_parts.append(indented_output)
        report_parts.append("---------------------------\n")

    if test_result.errors and test_result.errors != "None":
        report_parts.append("--- Summary Errors ---")
        indented_errors = "\n".join([f"  {line}" for line in test_result.errors.split('\n')])
        report_parts.append(indented_errors)
        report_parts.append("--------------------\n")

    full_report = "\n".join(report_parts)
    return f"{"=" * 60}\n{full_report.strip()}\n{"=" * 60}"


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


def _run_test(test_func, timeout=60, test_args=(), test_name=""):
    """Helper function to run an individual test and return a TestOutput object."""
    user_output_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(user_output_buffer):
            set_timeout(timeout)
            result = test_func(*test_args, test_name)
            reset_timeout()
        
        result.name = test_name
        result.user_output = user_output_buffer.getvalue()
        return result
        
    except TimeoutException:
        return TestOutput(
            name=test_name,
            score=0,
            max_score=1,
            description=f"Could not run the test because it timed out after {timeout} seconds.",
            errors=f"{test_name} - TIMEOUT ({timeout}s)",
            output="",
            user_output=user_output_buffer.getvalue()
        )
    except Exception:
        tb = traceback.format_exc()
        return TestOutput(
            name=test_name,
            score=0,
            max_score=1,
            description="Could not run the test because it failed due to a runtime error.",
            errors=f"{test_name} - RUNTIME ERROR:\n{tb}",
            output="",
            user_output=user_output_buffer.getvalue()
        )


def run_all_tests(tests, timeout=60):
    results = []

    overall_score = 0
    overall_max = 0

    for f, args, name in tests:
        test_result = _run_test(f, timeout, args, name)
        
        overall_score += test_result.score
        overall_max += test_result.max_score
        results.append(test_result)

    return results, overall_score, overall_max
