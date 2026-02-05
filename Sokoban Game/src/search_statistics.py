class SearchStatistics:
    """
    A class used to track and display statistics related to the search problem
    in question.
    """

    def __init__(self,
                 n_expanded: int,
                 n_generated: int,
                 n_pruned_cycles: int,
                 pruned_cost: int,
                 total_time: int):
        """
        :param n_expanded: the number of expanded nodes.
        :param n_generated: the number of generated nodes.
        :param n_pruned_cycles: the number of pruned cycles.
        :param pruned_cost: the total pruned cost of this search problem.
        :param total_time: the total time taken by this search problem.
        """
        self.states_expanded = n_expanded
        self.states_generated = n_generated
        self.states_pruned_cycles = n_pruned_cycles
        self.states_pruned_cost = pruned_cost
        self.total_time = total_time

    def __str__(self) -> str:
        return f"states generated: {self.states_generated}\n" + \
            f"states explored: {self.states_expanded}\n" + \
            f"state pruned by cycle checking: {self.states_pruned_cycles}\n" + \
            f"states pruned by cost checking: {self.states_pruned_cost}\n" + \
            f"total search time: {self.total_time}\n"
