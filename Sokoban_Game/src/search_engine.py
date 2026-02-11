import os

from typing import Tuple

from .search_statistics import SearchStatistics
from .search_node import *
from .search_constants import (
    _BREADTH_FIRST_STR,
    _DEPTH_FIRST,
    _CC_DEFAULT_STR,
    _SEARCH_STRATEGY_MAP,
    _CC_PATH, _CC_FULL, _CC_PATH_STR,
    _CYCLE_CHECK_MAP
)

# Zero Heuristic Function---for uninformed search don't include heur_fn
# in call to search engine's search method, defaults heur_fn to the zero fn.
def _zero_hfn(state):
    '''Null heuristic (zero)'''
    return 0

def _fval_function(state):
    '''default fval function results in Best First Search'''
    return state.hval

class SearchEngine:
    """
    A search engine that traverses a graph formed by SearchNodes.
    Nodes contain problem states defined by StateSpace objects, with
    unexpanded nodes stored in an OpenNodeCollection.

    This class defines the main set of routines that will be used by the user,
    including setting the search strategy, invoking search, and resuming search
    after a goal is found.
    """

    def __init__(self, strategy: str = _BREADTH_FIRST_STR, cc: str = _CC_DEFAULT_STR):
        """
        :param strategy: the search strategy used to expand nodes in the search problem.
        :param cc_level: the level at which cycles will be checked.
        """
        self.strategy = -1
        self.cc = -1
        self.n_cc_pruned = 0
        self.n_cost_pruned = 0
        self.trace = 0

        self.open_nodes = None
        self.path_to_gval = {}

        self.goal_fn = None
        self.heur_fn = None
        self.fval_function = None

        self.search_start_time = -1
        self.search_stop_time = -1

        self.set_strategy(strategy)
        self.set_cycle_check(cc)

    def init_statistics(self) -> None:
        """
        Initialize the statistics used for tracking search progress.
        """
        SearchNode.n = 0
        StateSpace.n = 1  # initial state already generated

    def trace_on(self, level: int = 1) -> None:
        """
        Used for debugging. Allows for two levels of verbosity,
        i.e. path-checking at level = 1,
             or full cycle-checking at level = 2.
        """
        self.trace = level

    def trace_off(self) -> None:
        self.trace = 0

    def set_strategy(self, strategy: str = _BREADTH_FIRST_STR) -> None:
        if strategy not in _SEARCH_STRATEGY_MAP.keys():
            raise ValueError(f"Unknown search strategy '{strategy}'.\n" + \
                  f"Must be one of: {_SEARCH_STRATEGY_MAP.keys()}.\n" + \
                  f"Setting to {_BREADTH_FIRST_STR}.")

        self.strategy = _SEARCH_STRATEGY_MAP[strategy]

    def set_cycle_check(self, cc: str = _CC_DEFAULT_STR):
        if cc not in _CYCLE_CHECK_MAP.keys():
            raise ValueError(f"Unknown cycle check level '{cc}'.\n" + \
                  f"Must be one of: {_CYCLE_CHECK_MAP.keys()}.\n" + \
                  f"Setting to {_CC_PATH_STR}-level.")

        if cc == _CC_DEFAULT_STR and self.strategy == _DEPTH_FIRST:
            self.cc = _CC_PATH
        else:
            self.cc = _CYCLE_CHECK_MAP[cc]
                

    def get_strategy(self) -> str:
        inverted_strategies = {i: strat for strat, i in _SEARCH_STRATEGY_MAP.items()}
        strategy = inverted_strategies[self.strategy]

        inverted_cycles = {i: cc for cc, i in _CYCLE_CHECK_MAP.items()}
        cc = inverted_cycles[self.cc]

        return f"{strategy} with {cc} cycle checking"

    def init_search(
            self,
            init_state: 'StateSpace',
            goal_fn: Callable,
            heur_fn: Callable = _zero_hfn,
            fval_fn: Callable = _fval_function
    ) -> None:
        """
        Get ready to search. Call search on this object to run the search.

        :param init_state: the state of the puzzle to start the search from.
        :param goal_fn: the goal function for the puzzle
        :param heur_fn: the heuristic function to use (only relevant for search strategies that use heuristics)
        :param fval_fn: the f-value function (only relevant for custom search strategy)
        """
        # Perform full cycle checking as follows
        # a. check state before inserting into OPEN. If we had already reached
        #   the same state via a cheaper path, don't insert into OPEN.
        # b. Sometimes we find a new cheaper path to a state (after the older
        #   more expensive path to the state has already been inserted.
        #   We deal with this lazily. We check states extracted from OPEN
        #   and if we have already expanded that state via a cheaper path
        #   we don't expand it. If we had expanded the state via a more
        #   expensive path, we re-expand it.

        self.init_statistics()

        if self.trace:
            print("   TRACE: Search Strategy: ", self.get_strategy())
            print("   TRACE: Initial State: ", end="")
            init_state.print_state()
        self.open_nodes = OpenNodeCollection(self.strategy)

        node = SearchNode(init_state, heur_fn(init_state), fval_fn)

        # the cycle check dictionary stores the cheapest path (g-val) found
        # so far to a state.
        if self.cc == _CC_FULL:
            self.path_to_gval[init_state.hashable_state()] = init_state.gval

        self.open_nodes.insert(node)
        self.fval_function = fval_fn
        self.goal_fn = goal_fn
        self.heur_fn = heur_fn

    def search(
            self,
            timebound: int = None,
            costbound: Tuple[int, int, int] = None
    ) -> (StateSpace | bool, 'SearchStatistics'):
        """
        Start searching, using the parameters set by init_search. Assuming a
        solution is found, this will return a goal path as well as a
        SearchStatistics object.

        :param timebound: the maximum amount of time, in seconds, to spend on this search.
        :param costbound: the cost bound 3-tuple for pruning, as specified in the assignment.
        """

        self.search_start_time = os.times()[0]
        self.search_stop_time = None

        if timebound:
            self.search_stop_time = self.search_start_time + timebound

        goal_node = self._searchOpen(self.goal_fn, self.heur_fn, costbound)

        total_search_time = os.times()[0] - self.search_start_time
        stats = SearchStatistics(
            SearchNode.n,
            StateSpace.n,
            self.n_cc_pruned,
            self.n_cost_pruned,
            total_search_time
        )

        if goal_node:
            return goal_node.state, stats
        else:  # exited the while without finding goal---search failed
            return False, stats

    def _searchOpen(
            self,
            goal_fn: Callable,
            heur_fn: Callable,
            costbound: Tuple[int, int, int]
    ) -> SearchNode | bool:
        """
        Search, starting from self.open_nodes.

        :param goal_fn: the goal function.
        :param heur_fn: the heuristic function.
        :param fval_function: the f-value function (only relevant when using a custom search strategy).
        :param costbound: the cost bound 3-tuple, as described in the assignment.
        """
        if self.trace:
            print(f"   TRACE: Initial OPEN: {self.open_nodes.print_open()}")
            if self.cc == _CC_FULL:
                print(f"   TRACE: Initial CC_Dict: {self.path_to_gval}")

        while not self.open_nodes.is_empty():
            node = self.open_nodes.extract()

            if self.trace:
                print(
                    f"   TRACE: Next State to expand: \n" + \
                    f"<S{node.state.index}:" + \
                    f"{node.state.action}:" + \
                    f"{node.state.hashable_state()}, \n" + \
                    f"g={node.gval}, h={node.hval}, f=g+h={node.gval + node.hval}>"
                )
                if node.state.gval != node.gval:
                    print("ERROR: node.gval != node.gval!")

            if goal_fn(node.state):
                return node
            if self.search_stop_time:
                if os.times()[0] > self.search_stop_time:
                    # exceeded time bound, must terminate search
                    print("Search has exceeded the time bound provided.")
                    return False

            # All states reached by a search node on OPEN have already
            # been hashed into the self.cc_dictionary. However,
            # before expanding a node we might have already expanded
            # an equivalent state with lower g-value. So only expand
            # the node if the hashed g-value is no greater than the
            # node's current g-value.

            if self.trace:
                if self.cc == _CC_FULL:
                    print(
                        f"   TRACE: CC_dict gval=" + \
                        f"{self.path_to_gval[node.state.hashable_state()]}, " +\
                        f"node.gval={node.gval}"
                    )

            if (
                    self.cc == _CC_FULL
                    and self.path_to_gval[node.state.hashable_state()] < node.gval
            ):
                continue

            successors = node.state.successors()

            if self.trace:
                print("   TRACE: Expanding Node. Successors = ")
                for succ in successors:
                    print(
                        f"<S{succ.index}:{succ.action}:{succ.hashable_state()}, " + \
                        f"g={succ.gval}, h={heur_fn(succ)}, f=g+h={succ.gval + heur_fn(succ)}>"
                    )

            for succ in successors:
                hash_state = succ.hashable_state()
                if self.trace > 1:
                    if self.cc == _CC_FULL and hash_state in self.path_to_gval.keys():
                        print(
                            f"   TRACE: Already in CC_dict, " + \
                            f"CC_dict gval={self.path_to_gval[hash_state]}, " + \
                            f"successor state gval={succ.gval}"
                        )
                    print("   TRACE: Successor State:")
                    succ.print_state()
                    print(f"   TRACE: Heuristic Value: {heur_fn(succ)}")

                    if self.cc == _CC_FULL and hash_state in self.path_to_gval.keys():
                        print(
                            f"   TRACE: Already in CC_dict, " + \
                            f"CC_dict gval={self.path_to_gval[hash_state]}, " + \
                            f"successor state gval={succ.gval}"
                        )

                    if self.cc == _CC_PATH and succ.has_path_cycle():
                        print("   TRACE: On cyclic path")

                if self.is_prunable(succ):
                    self.n_cc_pruned = self.n_cc_pruned + 1
                    if self.trace > 1:
                        print(" TRACE: Successor State pruned by cycle checking")
                        print("\n")
                    continue

                succ_hval = heur_fn(succ)
                if (
                        costbound is not None
                        and
                        (
                                succ.gval > costbound[0]
                                or succ_hval > costbound[1]
                                or succ.gval + succ_hval > costbound[2]
                        )
                ):
                    self.n_cost_pruned = self.n_cost_pruned + 1
                    if self.trace > 1:
                        print(f" TRACE: Successor State pruned, over current cost bound of {costbound}")
                    continue

                    # passed all cycle checks and costbound checks ...add to open
                self.open_nodes.insert(
                    SearchNode(succ, succ_hval, node.fval_function)
                )

                if self.trace > 1:
                    print(" TRACE: Successor State added to OPEN")
                    print("\n")

                # record cost of this path in dictionary.
                if self.cc == _CC_FULL:
                    self.path_to_gval[hash_state] = succ.gval

        # end of while--OPEN is empty and no solution
        return False

    def is_prunable(self, successor: 'StateSpace') -> bool:
        """
        Return whether the given successor state can be pruned from the search.j
        :param successor: the successor state whose prunability needs to be checked
        """
        successor_hash = successor.hashable_state()
        contains_full_cycle = \
            (
                    self.cc == _CC_FULL
                    and successor_hash in self.path_to_gval.keys()
                    and successor.gval > self.path_to_gval[successor_hash]
            )
        contains_path_cycle = self.cc == _CC_PATH and successor.has_path_cycle()

        return contains_full_cycle or contains_path_cycle
