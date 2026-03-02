from typing import Any

class Constraint:
    """
    A constraint in the CSP. Specifies an ordering over Variable objects,
    which is used to determine if a variable assignment satisfies the
    constraint as defined by its scope.

    Constraints are implemented by storing a set of satisfying tuples.
    Specifically, each tuple specifies a value for each variable in the
    scope such that the sequence of values satisfies the constraint.

    # TODO : Better explain the type of the tuple users can expect to see
    """

    def __init__(self, name: str, scope: list['Variable']):
        """
        :param name: the name of this constraint
        :param scope: the scope of this constraint, represented as an
                      ordered list of Variable objects
        """

        self.scope = list(scope)
        self.name = name

        # The set of satisfying tuples.
        self.sat_tuples = dict()

        # Used in GAC propagation to define a list of satisfying
        # tuples that contain a particular (variable, value) pair.
        self.sup_tuples = dict()

    def __str__(self) -> str:
        return f"{self.name}({[var.name for var in self.scope]})"

    # TODO: Determine the type of tuples
    def add_satisfying_tuples(self, tuples):
        """
        Add all satisfying tuples in the given list tuples.
        """
        for x in tuples:
            # TODO: tuples are by definition immutable. this shouldn't be necessary.
            tup = tuple(x)  # ensure we have an immutable tuple

            # TODO: Is this line logically correct?
            # should it be..
            #   tup not in self.sat_tuples
            # ?
            # not tup in ____
            #   is not the same as
            # t not in ____
            if not tup in self.sat_tuples:
                self.sat_tuples[tup] = True

            # Assign tup as a supporting tuple for each variable value
            for i, val in enumerate(tup):
                var = self.scope[i]
                if not (var,val) in self.sup_tuples:
                    self.sup_tuples[(var,val)] = []
                self.sup_tuples[(var,val)].append(tup)

    def get_scope(self) -> list['Variable']:
        """
        Return the scope of this constraint.
        """
        return list(self.scope)

    def check(self, vals: list[Any]) -> bool:
        """
        Return true iff the ordered value assignment defined by vals
        satisfies self as defined by the constraint satisfaction problem.
        """
        return tuple(vals) in self.sat_tuples

    def get_n_unassigned_vars(self) -> int:
        """
        Return the number of unassigned variables in the scope defined by self.
        """
        n = 0
        for v in self.scope:
            if not v.is_assigned():
                n = n + 1
        return n

    def get_unassigned_vars(self) -> list['Variable']:
        """
        Return the list of unassigned variables in the scope defined by self.

        Note: this is more computationally costly than self.get_n_unassigned_vars()
        """
        vs = []
        for v in self.scope:
            if not v.is_assigned():
                vs.append(v)
        return vs

    def has_support(self, var: 'Variable', val: Any) -> bool:
        """
        Return true iff (var, val) has a supporting tuple in self.

        In other words, (var, val) has support iff it has a set of
        assignments satisfying the constraint, where each value is still
        in the corresponding variables current domain.
        """
        if (var, val) in self.sup_tuples:
            for t in self.sup_tuples[(var, val)]:
                if self.tuple_is_valid(t):
                    return True
        return False

    # TODO: Determine the type of t
    def tuple_is_valid(self, t) -> bool:
        """
        Return true iff tuple t is in the current domain of
        every variable in the scope defined by self.
        """
        for i, var in enumerate(self.scope):
            if not var.in_cur_domain(t[i]):
                return False
        return True

