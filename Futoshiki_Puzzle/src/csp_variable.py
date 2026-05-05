from typing import Any

class Variable:
    """
    A variable in a given CSP, composed of a name and a list of domain values.
    Values can always be added to the domain, but they cannot be removed.

    Variables implement the concept of a current domain with a list[bool] of flags
    indicating which values in the total domain are current, i.e. unpruned. Values
    can be pruned and restored, and variables can be queried for values in the
    current domain. Variables can also be queried for the count of remaining
    values in the current domain.

    Variables can be assigned/unassigned to a value from the domain. Assignment does not
    affect the internal state of the current domain, meaning that there are no
    side effects during search such as pruning and restoring. When a variable is assigned,
    the current domain is effectively reduced to the assigned value. The purpose of this
    is to simplify propagator implementation.
    """

    def __init__(self, name: str, domain: list[Any] = []):
        """
        :param name: name of the variable
        :param domain: initial list of domain values
        """
        self.name = name
        self.dom = list(domain)
        self.curdom = [True] * len(domain)
        self.assignedValue = None

    def __repr__(self):
        return "Variable --\"{}\"".format(self.name)

    def __str__(self):
        return "Variable --\"{}\"".format(self.name)

    def add_domain_values(self, values: list[Any]):
        """
        Appends all values in values to the domain of this variable.
        """
        for val in values:
            self.dom.append(val)
            self.curdom.append(True)

    def domain_size(self) -> int:
        """
        Return the size of the permanent domain.
        """
        return len(self.dom)

    def domain(self) -> list[Any]:
        """
        Return the permanent domain.
        """
        return list(self.dom)

    def prune_value(self, value: Any):
        """
        Remove value from the current domain.
        """
        self.curdom[self._value_index(value)] = False

    def unprune_value(self, value: Any):
        """
        Restore value into the current domain.
        """
        self.curdom[self._value_index(value)] = True

    def cur_domain(self) -> list[Any]:
        """
        Return the list of values in the current domain.

        If self is assigned, then self's assigned value
        is the only value in the current domain.
        """
        vals = []
        if self.is_assigned():
            vals.append(self.get_assigned_value())
        else:
            for i, val in enumerate(self.dom):
                if self.curdom[i]:
                    vals.append(val)
        return vals

    def in_cur_domain(self, value: Any) -> bool:
        """
        Return True iff value is in the current domain.

        If self is assigned, then self's assigned value
        is the only value in the current domain. In other words,
        return True iff self is assigned to value.
        """
        if not value in self.dom:
            return False
        if self.is_assigned():
            return value == self.get_assigned_value()
        else:
            return self.curdom[self._value_index(value)]

    def cur_domain_size(self) -> int:
        """
        Return the size of the current domain.
        """
        if self.is_assigned():
            return 1
        else:
            return sum(1 for v in self.curdom if v)

    def restore_curdom(self):
        """
        Restore all values back into the current domain.
        """
        for i in range(len(self.curdom)):
            self.curdom[i] = True

    def is_assigned(self) -> bool:
        """
        Return True iff self is assigned.
        """
        return self.assignedValue is not None

    def assign(self, value: Any):
        """
        Assign the given value to self. Used in bt_search.

        During assignment, all other values are removed from the current
        domain. This is reversed when self is unassigned.
        """
        if self.is_assigned():
            print(f"ERROR: {str(self)} is already assigned")
            return
        elif not self.in_cur_domain(value):
            print(f"ERROR: {value} is not in the current domain")
            return

        self.assignedValue = value

    def unassign(self):
        """
        Unassign the value currently assigned to self and restore
        the current domain.
        """
        if not self.is_assigned():
            print(f"ERROR: {str(self)} is not assigned")
            return
        self.assignedValue = None

    def get_assigned_value(self):
        """
        Return the assigned value of self, or None if self is unassigned.
        """
        return self.assignedValue


    def _value_index(self, value):
        """
        Return the index of value within self's domain.
        """
        return self.dom.index(value)

    def _print_all(self):
        """
        Print out the total domain and the current domain of self.
        """
        print(
            "Variable --\"{}\": Domain = {}, Current Domain = {}".format(
                self.name,
                self.dom,
                self.curdom)
        )
