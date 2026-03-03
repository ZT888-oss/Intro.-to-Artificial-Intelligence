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
    pruned = []
    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)

    for con in constraints:
        # Forward checking: exactly one unassigned variable
        if con.get_n_unassigned_vars() == 1:
            var = con.get_unassigned_vars()[0]

            for val in var.cur_domain()[:]:  # iterate over copy
                if not con.has_support(var, val):
                    var.prune_value(val)
                    pruned.append((var, val))

            # Domain wipe-out check
            if var.cur_domain_size() == 0:
                return False, pruned

    return True, pruned

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
    pruned = []
    if newVar is None:
        gac_queue = list(csp.get_all_cons())
    else:
        gac_queue = list(csp.get_cons_with_var(newVar)) 
    while gac_queue:
        con = gac_queue.pop(0)

        for var in con.get_scope():
            for val in var.cur_domain()[:]:  # iterate over copy
                if not con.has_support(var, val):
                    var.prune_value(val)
                    pruned.append((var, val))
                    
                    # Domain wipe-out
                    if var.cur_domain_size() == 0:
                        return False, pruned

                    # Re-enqueue all constraints involving var (except con already processed)
                    for c in csp.get_cons_with_var(var):
                        if c not in gac_queue:
                            gac_queue.append(c)
                            
    return True, pruned
        

def ord_mrv(csp: 'CSP') -> 'Variable':
    """
    Return the next variable to be assigned in csp according to the
    Minimum Remaining Values heuristic.

    That is, return the variable with the most constraint current domain,
    i.e. the variable with the fewest legal values.
    """
    # TODO: Implement
    unassigned_vars = csp.get_all_unasgn_vars()

    mrv_var = None
    smallest_domain = float('inf')

    for var in unassigned_vars:
        domain_size = var.cur_domain_size()

        if domain_size < smallest_domain:
            smallest_domain = domain_size
            mrv_var = var

    return mrv_var
