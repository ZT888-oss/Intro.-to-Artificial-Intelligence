"""
General notes to consider:
    * Propagator functions return a tuple of the shape
            True/False, [(Variable, value), ...]
      where False indicates that the propagator has reached
      a dead-end (in which case `bt_search` will backtrack),
      and True otherwise.

    * Propagator functions should not prune a value that has already
      been pruned.
      
    * `csp` is a required argument that represents the complete
      constraint satisfaction problem. Propagation functions will use
      this argument to access the variables and constraints that define
      the problem. Please read through the source code:
            `src/`
                `backtracking.py`
                `csp.py`
                `csp_constraint.py`
                `csp_variable.py`

    * `newVar` is an optional argument that represents the
      variable that has been most-recently assigned during search.
      If it is None, then the dedicated propagation algorithm will
      employ the logic described in the corresponding docstring
      to continue searching.
"""
from typing import Any


def prop_BT(csp: 'CSP', newVar: 'Variable' = None) -> tuple[bool, list[tuple['Variable', Any]]]:
    """
    Return a tuple consisting of a boolean that represents whether we can
    continue propagating and the associated list of (Variable, Value) pairs
    that were pruned during propagation.

    If backtracking is called without a newly-instantiated variable,
    do nothing. That is, return (True, []).

    If backtracking is called with a newly-instantiated variable, check
    the satisfiability of every constraint whose scope contains newVar
    and whose variables are fully assigned.

    :param csp: the constraint satisfaction problem
    :param newVar: the most recently assigned variable
    """

    if not newVar:
        return True, []
    for constraint in csp.get_cons_with_var(newVar):
        if constraint.get_n_unassigned_vars() == 0:
            values = []
            variables = constraint.get_scope()
            for variable in variables:
                values.append(variable.get_assigned_value())
            if not constraint.check(values):
                return False, []
    return True, []


def prop_FC(csp: 'CSP', newVar: 'Variable' = None) -> tuple[bool, list[tuple['Variable', Any]]]:
    """
    Return a tuple consisting of a boolean that represents whether we can
    continue propagating and the associated list of (Variable, Value) pairs
    that were pruned during propagation.

    If forward-checking is called without a newly-instantiated variable,
    forward-check the satisfiability of all unary constraints: that is,
    constraints whose scope contains only one variable that is unassigned.

    If forward-checking is called with a newly-instantiated variable,
    forward-check the satisfiability of unary constraints whose scope
    contains newVar.

    :param csp: the constraint satisfaction problem
    :param newVar: the most recently assigned variable
    """
    # TODO: Implement
    raise NotImplementedError("prop_FC not implemented")


def prop_GAC(csp: 'CSP', newVar: 'Variable' = None) -> tuple[bool, list[tuple['Variable', Any]]]:
    """
    Return a tuple consisting of a boolean that represents whether we can
    continue propagating and the associated list of (Variable, Value) pairs
    that were pruned during propagation.
    
    If GAC is called without a newly-instantiated variable, initialize the GAC
    queue with all constraints in csp.

    If GAC is called with a newly-instantiated variable, initialize the GAC
    queue with all constraints in csp that whose scope contains newVar.

    :param csp: the constraint satisfaction problem
    :param newVar: the most recently assigned variable
    """
    # TODO: Implement
    raise NotImplementedError("prop_GAC not implemented")



def ord_mrv(csp: 'CSP') -> 'Variable':
    """
    Return the next variable to be assigned in csp according to the
    Minimum Remaining Values heuristic.

    That is, return the variable with the most constraint current domain,
    i.e. the variable with the fewest legal values.
    """
    # TODO: Implement
    raise NotImplementedError("ord_mrv not implemented")
