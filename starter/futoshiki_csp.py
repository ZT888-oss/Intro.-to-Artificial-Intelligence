"""
General notes to consider:
    * The input to these model-generating functions is shaped
      like the following example:

            e.g.
                 [[0,>,0,.,2],
                  [0,.,0,.,0],
                  [0,.,0,<,0]]

            0             -  an empty cell
            .             -  no inequality constraint
            <             -  left cell less than right cell
            >             -  left cell greater than rightcell
            range(1,n+1)  -  pre-set value at this position

      This grid represents the following Futoshiki board:

            e.g.
                -------------
                | _ > _ | 2 |
                | _ | _ | _ |
                | _ | _ < _ |
                -------------

      Note that the input is hence a list of lists where each inner list
      of length 2n - 1 represents a row of the board, where n is the dimension
      of the board.

    * Both models return a tuple (csp, variables):

      csp        - the CSP object representing the Futoshiki game
      variables  - a list of lists of variables corresponding to the
                   solved variables for csp. This list of lists is how
                   the solution to the csp is accessed.

    * An example of how models can be used in conjunction with the
      provided backend:

            e.g.
                 csp, variables = futoshiki_csp_model_1(board)
                 solver = BT(csp)
                 solver.bt_search(prop_FC)

      Upon completion of search, `variables[0][0].get_assigned_value()`
      will return the correct value in the top-left cell of the Futoshiki board.

"""

from typing import Any
from src import Variable, Constraint, CSP, BacktrackingSearch


def futoshiki_csp_model_1(grid: list[list[Any]]) -> tuple['CSP', list[list['Variable']]]:
    """
    Return a tuple consisting of the constraint satisfaction problem constructed
    according to the input Futoshiki puzzle grid, and a list of lists of Variable
    objects that represents the matrix of values corresponding to the input grid
    indexed from (0, 0) to (n-1, n-1).

    Constraints for model 1 are built using only binary inequality for both rows
    and columns. That is, all constraints are fixed to two variables in scope.

    :param grid: a list of lists of objects representing the Futoshiki grid, e.g.
                    grid = [[0,>,0,.,2], [0,.,0,.,0], [0,.,0,<,0]]
    """
    # TODO: Implement
    raise NotImplementedError("Futoshiki CSP Model 1 not implemented")

def futoshiki_csp_model_2(grid: list[list[Any]]) -> tuple['CSP', list[list['Variable']]]:
    """
    Return a tuple consisting of the constraint satisfaction problem constructed
    according to the input Futoshiki puzzle grid, and a list of lists of Variable
    objects that represents the matrix of values corresponding to the input grid
    indexed from (0, 0) to (n-1, n-1).

    Constraints for model 2 are built using n-ary all-different constraints
    for both rows and columns. That is, there are 2*n + k total constraints:
    n all-different constraints for rows, n all-different constraints for columns,
    and k binary inequality constraints for the inequalities on the board.

    :param grid: a list of lists of objects representing the Futoshiki grid, e.g.
                    grid = [[0,>,0,.,2], [0,.,0,.,0], [0,.,0,<,0]]
    """
    # TODO: Implement
    raise NotImplementedError("Futoshiki CSP Model 2 not implemented")