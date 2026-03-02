import time
from typing import Callable, Any

class BacktrackingSearch:
    """
    A class to encapsulate backtracking search with statistics tracking
    and domain pruning/unpruning for CSP solving.

    This class provides functionality for plain backtracking, forward-checking,
    and generalized arc consistency (GAC) depending on the propagator used.
    """

    def __init__(self, csp: 'CSP'):
        """
        Initialize the backtracking search object.

        :param csp: the constraint satisfaction problem
        """
        self.csp = csp
        self.num_decisions = 0  # Number of variable assignments made during search
        self.num_prunings = 0  # Number of value prunings during search
        self.unassigned_variables = []  # Track unassigned variables
        self.trace_enabled = False
        self.runtime = 0

    def enable_trace(self):
        """
        Enable search trace output.
        """
        self.trace_enabled = True

    def disable_trace(self):
        """
        Disable search trace output.
        """
        self.trace_enabled = False

    def clear_statistics(self):
        """
        Reset all search statistics counters.
        """
        self.num_decisions = 0
        self.num_prunings = 0
        self.runtime = 0

    def print_statistics(self):
        """
        Print search statistics.
        """
        print(f"Search made {self.num_decisions} variable assignments and "
              f"pruned {self.num_prunings} variable values")

    def restore_pruned_values(self, pruned_values: list[tuple['Variable', Any]]):
        """
        Restore a list of values to variable domains.

        :param pruned_values: list of (variable, value) pairs to restore
        """
        for variable, value in pruned_values:
            variable.unprune_value(value)

    def restore_all_domains(self):
        """
        Reinitialize all variable domains to their original state.
        """
        if self.csp is not None:
            for variable in self.csp.variables:
                if variable.is_assigned():
                    variable.unassign()
                variable.restore_curdom()

    def restore_unassigned_variable(self, variable: 'Variable'):
        """
        Add variable back to the list of unassigned variables.

        :param variable: variable to add back to unassigned list
        """
        self.unassigned_variables.append(variable)

    def search(
            self,
            propagator: Callable,
            variable_ordering: Callable = None,
            value_ordering: Callable = None):
        """
        Solve the CSP using the specified propagator routine.

        Note:
            The propagator should NOT prune values that are already pruned
            or prune the same value multiple times.

        :param propagator: function with signature propagator(csp, newly_assigned_var=None)
                           Returns (bool, [(Variable, Value), ...])
                            - bool: True if search can continue, False if deadend detected
                            - list: All (variable, value) pairs pruned by the propagator
        :param variable_ordering: Optional function to determine variable assignment order
        :param value_ordering: Optional function to determine value assignment order
        """
        if self.csp is None or propagator is None:
            return

        self.clear_statistics()
        start_time = time.process_time()

        # Initialize domains and unassigned variables
        self.restore_all_domains()
        self.unassigned_variables = [var for var in self.csp.variables
                                     if not var.is_assigned()]

        # Initial propagation with no assigned variables
        propagation_successful, initial_prunings = propagator(self.csp)

        if initial_prunings is None:
            return

        self.num_prunings += len(initial_prunings)

        if self.trace_enabled:
            print(f"{len(self.unassigned_variables)} unassigned variables at start")
            print(f"Root Prunings: {initial_prunings}")

        if not propagation_successful:
            print(f"CSP {self.csp.name} detected contradiction at root")
            search_successful = False
        else:
            # Perform recursive backtracking search
            search_successful = self._recursive_search(
                propagator, variable_ordering, value_ordering, depth=1
            )

        # Restore initial prunings
        self.restore_pruned_values(initial_prunings)

        # Print results
        if not search_successful:
            print(f"CSP {self.csp.name} unsolved. Has no solutions")
        else:
            elapsed_time = time.process_time() - start_time
            print(f"CSP {self.csp.name} solved. CPU Time used = {elapsed_time}")
            self.csp.print_soln()

        print("Backtracking search finished")
        self.print_statistics()

    def _recursive_search(
            self,
            propagator: Callable,
            variable_ordering: Callable,
            value_ordering: Callable,
            depth: int) -> bool:
        """
        Recursive backtracking search implementation.

        :param propagator: constraint propagation function
        :param variable_ordering: variable selection heuristic
        :param value_ordering: value selection heuristic
        :param depth: current search depth (for tracing)
        """
        if self.trace_enabled:
            print('  ' * depth + f"recursive_search depth {depth}")

        # Base case: all variables assigned
        if not self.unassigned_variables:
            return True

        # Select next variable to assign
        if variable_ordering:
            selected_variable = variable_ordering(self.csp)
        else:
            selected_variable = self.unassigned_variables[0]

        self.unassigned_variables.remove(selected_variable)

        if self.trace_enabled:
            print('  ' * depth + f"Selected variable: {selected_variable}")

        # Determine value ordering
        if value_ordering:
            domain_values = value_ordering(self.csp, selected_variable)
        else:
            domain_values = selected_variable.cur_domain()

        # Try each value in the domain
        for value in domain_values:
            if self.trace_enabled:
                print('  ' * depth + f"Trying {selected_variable} = {value}")

            # Make assignment
            selected_variable.assign(value)
            self.num_decisions += 1

            # Propagate constraints
            propagation_successful, pruned_values = propagator(self.csp, selected_variable)
            self.num_prunings += len(pruned_values)

            if self.trace_enabled:
                print('  ' * depth + f"Propagation successful: {propagation_successful}")
                print('  ' * depth + f"Pruned values: {pruned_values}")

            # If propagation successful, recurse
            if propagation_successful:
                if self._recursive_search(propagator, variable_ordering,
                                          value_ordering, depth + 1):
                    return True

            # Backtrack: restore pruned values and unassign variable
            if self.trace_enabled:
                print('  ' * depth + f"Backtracking, restoring: {pruned_values}")

            self.restore_pruned_values(pruned_values)
            selected_variable.unassign()

        # All values tried unsuccessfully, restore variable to unassigned list
        self.restore_unassigned_variable(selected_variable)
        return False