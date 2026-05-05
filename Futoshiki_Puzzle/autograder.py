#!/usr/bin/env python3
import tests

import argparse
import test_utils

# --- Autograder Configuration ---
# These constants can be easily changed for different assignments.

# Name of the assignment (used in messages and UI)
ASSIGNMENT_NAME = "A2 - Futoshiki"

# The Python module where test cases are defined (e.g., "tests" for tests.py)
TEST_MODULE_NAME = "tests"

# The variable name within TEST_MODULE_NAME that holds the list of tests.
# Tests should be a list of tuples: (function, args_tuple, "test_name_string")
TEST_LIST_VARIABLE_NAME = "futoshiki_tests"

# Default timeout for each individual test in seconds
DEFAULT_TIMEOUT_SECONDS = 60

# --- End Autograder Configuration ---


def main():
    parser = argparse.ArgumentParser(description=f"Run {ASSIGNMENT_NAME} autograder.")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--test", "-t", nargs="+",
        help="Specify one or more test names to run (e.g. test_simple_fc "
             "test_tiny_adder_fc). If omitted, all tests will be run.")
    args = parser.parse_args()

    print(f"Running {ASSIGNMENT_NAME} Autograder...\n")

    all_tests = test_utils.load_tests_from_module(
        TEST_MODULE_NAME, TEST_LIST_VARIABLE_NAME)

    if not all_tests:
        print("No tests were loaded. Exiting.")
        return

    tests_to_run = []

    # If the user provided specific test names, filter out tests not matching those names.
    if args.test:
        specified_test_names = set(args.test)
        tests_to_run = [t for t in all_tests if t[2] in specified_test_names]
        if not tests_to_run:
            print("No matching tests found for the provided names: "
                 f"{', '.join(specified_test_names)}. Available tests are:")
            for _, _, name in all_tests:
                print(f"  - {name}")
            print("Exiting.")
            return
        print(f"Running specified tests: {', '.join(specified_test_names)}\n")
    else:
        tests_to_run = all_tests
        print("Running all available tests...\n")

    results, overall_score, overall_max, group_scores, group_maxes = test_utils.run_all_tests(
        tests_to_run, DEFAULT_TIMEOUT_SECONDS)

    test_utils.print_report(results, args.verbose)

    # Print out the scores by section.
    print("\n----- Scores by Section -----")
    print("FC Score: %d/%d" % (group_scores.get("FC", 0), group_maxes.get("FC", 0)))
    print("GAC Score: %d/%d" % (group_scores.get("GAC", 0), group_maxes.get("GAC", 0)))
    print("Model 1 Score: %d/%d" % (group_scores.get("Model 1", 0), group_maxes.get("Model 1", 0)))
    print("Model 2 Score: %d/%d" % (group_scores.get("Model 2", 0), group_maxes.get("Model 2", 0)))
    print("Ord MRV Score: %d/%d" % (group_scores.get("Ord", 0), group_maxes.get("Ord", 0)))
    print("Total A3 Score: %d/%d" % (overall_score, overall_max))

    print("\nOverall Test Score: %d/%d" % (overall_score, overall_max))

    if not args.verbose:
        print("\nTo view detailed reports, re-run with --verbose flag.")
        print("To focus on a specific test, re-run with --test <test_name> flag.")


if __name__ == "__main__":
    main()