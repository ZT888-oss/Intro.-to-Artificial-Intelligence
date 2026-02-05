from typing import Optional, Any


class StateSpace:
    """
    An abstract base class for representing the states in a search
    space.  Each state has a pointer to the parent that was used to
    generate it, and the cost of g-value of the sequence of actions
    that was used to generate it.

    Equivalent states can be reached via different paths.
    To avoid exploring the same state multiple times, the search
    routines use cycle checking using hashing techniques. Hence,
    each StateSpace state (or object) must be able to return an
    immutable representation that uniquely represents the state and
    can be used to index into a dictionary.

    The StateSpace class must be specialized for the particular problem. Each
    particular problem will define a subclass of StateSpace that will also
    include information specific to that problem. See WaterJugs.py for an
    example, and the Class implementation for more details.
    """

    # Static variable for tracking number of transitions.
    n = 0

    def __init__(self, action: Optional[str], gval: float, parent: Optional['StateSpace']):
        """
        :param action: Action taken to reach this state; if this is the initial state,
                       then this will be "START"
        :param gval: Path cost from the start state
        :param parent: Parent state
        """
        self.action = action
        self.gval = gval
        self.parent = parent
        self.index = StateSpace.n
        StateSpace.n += 1

    def successors(self) -> list['StateSpace']:
        """
        Return a list of resulting_states reachable from this state.
        """
        raise NotImplementedError

    def hashable_state(self) -> Any:
        """
        Return a hashable representation of this state for state comparison and hashing.
        """
        raise NotImplementedError

    def print_state(self) -> None:
        """
        Print a human-readable description of this state.
        """
        raise NotImplementedError

    def print_path(self) -> None:
        """
        Print a human-readable graph of actions taken to reach this state.
        Can be overridden for more specific problems.
        """
        s = self
        states = []
        while s:
            states.append(s)
            s = s.parent
        states.pop().print_state()
        while states:
            print(" ==> ", end="")
            states.pop().print_state()

    def has_path_cycle(self) -> bool:
        """Returns True if self is equal to a prior state on its path"""
        s = self.parent
        hc = self.hashable_state()
        while s:
            if s.hashable_state() == hc:
                return True
            s = s.parent
        return False