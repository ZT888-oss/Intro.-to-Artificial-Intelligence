import heapq

from collections import deque
from typing import Callable

from .state import StateSpace
from .search_constants import (
    _DEPTH_FIRST, _BREADTH_FIRST, _BEST_FIRST, _ASTAR, _UCS, _CUSTOM,
    _SUM_HG, _H, _G, _C,
)

class SearchNode:
    """
    A node in the search problem, associated with a state in the search space.
    Each node is also associated with an h-value, a g-value, and a function
    used to compute it's f-value. We also store the number corresponding to this
    node in the sequence of nodes used to reach this one.
    """

    # Static variable used to track the number of this node.
    n = 0

    # Static variable used to define how comparison between nodes is
    # calculated. By default, we calculate based on the sum of h-value and g-value.
    lt_type = _SUM_HG

    def __init__(self, state: 'StateSpace', hval: int, fval_function: Callable):
        """
        :param state: the state of the search problem associated with this node.
        :param hval: the h-value of this node.
        :param fval_function: the function used to compute the f-val of this node.
        """
        self.state = state
        self.hval = hval
        self.gval = state.gval
        self.index = SearchNode.n
        self.fval_function = fval_function
        SearchNode.n = SearchNode.n + 1

    def __lt__(self, other: 'SearchNode') -> bool:
        """
        Return True if self is less than other. Comparison is defined by the
        static variable lt_type.
        Note that we break ties based on g-value, which allows for search to prioritize
        expansion along deeper paths.
        """

        if SearchNode.lt_type == _SUM_HG:
            if (self.gval + self.hval) == (other.gval + other.hval):
                # break ties using g-value
                return self.gval > other.gval
            else:
                return ((self.gval + self.hval) < (other.gval + other.hval))
        if SearchNode.lt_type == _G:
            return self.gval < other.gval
        if SearchNode.lt_type == _H:
            if self.hval == other.hval:
                return self.gval > other.gval
            return self.hval < other.hval
        if SearchNode.lt_type == _C:
            return self.fval_function(self) < other.fval_function(other)

        print('SearchNode class has invalid comparator setting!')

        # return default of lowest gval (generating UCS behavior)
        return self.gval < other.gval


class OpenNodeCollection:
    """
    A collection of unexpanded nodes in the search problem.
    """

    def __init__(self, search_strategy: int):
        """
        :param search_strategy: the strategy used to expand nodes in the search problem.
        """
        if search_strategy == _DEPTH_FIRST:
            # Uses a stack
            # LIFO: most recent successor
            self.open = []
            self.insert = self.open.append
            self.extract = self.open.pop
        elif search_strategy == _BREADTH_FIRST:
            # Uses a queue
            # FIFO oldest node not yet expanded
            self.open = deque()
            self.insert = self.open.append
            self.extract = self.open.popleft
        elif search_strategy == _UCS:
            # Uses a priority queue
            # First out is the node with the lowest g-value
            SearchNode.lt_type = _G
            self.open = []
            self.insert = lambda node: heapq.heappush(self.open, node)
            self.extract = lambda: heapq.heappop(self.open)
        elif search_strategy == _BEST_FIRST:
            # Uses a priority queue
            # First out is the node with the lowest h-value
            SearchNode.lt_type = _H
            self.open = []
            self.insert = lambda node: heapq.heappush(self.open, node)
            self.extract = lambda: heapq.heappop(self.open)
        elif search_strategy == _ASTAR:
            # Uses a priority queue
            # First out is the node with the lowest f-value, defined as g-value + h-value
            SearchNode.lt_type = _SUM_HG
            self.open = []
            self.insert = lambda node: heapq.heappush(self.open, node)
            self.extract = lambda: heapq.heappop(self.open)
        elif search_strategy == _CUSTOM:
            # Uses a priority queue
            # First out is the node with the lowest f-value, defined by the user
            SearchNode.lt_type = _C
            self.open = []
            self.insert = lambda node: heapq.heappush(self.open, node)
            self.extract = lambda: heapq.heappop(self.open)

    def is_empty(self):
        return not self.open

    def print_open(self):
        if len(self.open) == 1:
            print("   <S{}:{}:{}, g={}, h={}, f=g+h={}>".format(
                    self.open[0].state.index,
                self.open[0].state.action,
                self.open[0].state.hashable_state(),
                self.open[0].gval,
                self.open[0].hval,
                self.open[0].gval + self.open[0].hval),
                end=""
            )
        else:
            for nd in self.open:
                print("   <S{}:{}:{}, g={}, h={}, f=g+h={}>".format(
                    nd.state.index,
                    nd.state.action,
                    nd.state.hashable_state(),
                    nd.gval,
                    nd.hval,
                    nd.gval + nd.hval),
                    end=""
                )

