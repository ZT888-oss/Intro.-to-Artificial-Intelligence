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
    n = len(grid) #get row length
    variables = []       #holding name of each cell, V00, V02, V04...
    var_list = []
    for i in range(n):
          row_vars = []  #collect ro variabless for consisting a 2D lists
          for c in range(0, 2*n-1, 2):  #get value in each cell
            cell = grid[i][c]
            if cell == 0: #need to assign a value
                  domain = list(range(1,n+1)) 
            else:
                  domain = [cell]
            var = Variable(f"V{i}{c//2}", domain)
            
            var_list.append(var)
            row_vars.append(var)
      
          variables.append(row_vars)
            
    csp = CSP("futoshiki_csp_model_1", var_list)
      
    #No row contains more than one of the same number.
 
    for r in range(n):
            for c1 in range(n):     #now list avr_list is m by m lists that only contain value
                  for c2 in range(c1+1,n):
                        v1 = variables[r][c1]
                        v2 = variables[r][c2]
                        
                        if v1 != v2:
                              con = Constraint(f"Row_{r}_{c1}_{c2}", [v1, v2])
                              
                              tup = []
                              for a in v1.domain():
                                    for b in v2.domain():
                                          if a != b:
                                                tup.append((a, b))
                                    
                              con.add_satisfying_tuples(tup)
                              csp.add_constraint(con)
                        elif v1 == v2:
                              continue
                        
    # No column contains more than one of the same number.
    for r1 in range(n):
          for r2 in range(r1+1,n):
                for c in range(n):
                      v1 = variables[r1][c]
                      v2 = variables[r2][c]
                      
                      if v1 != v2:
                        con = Constraint(f"Col_{r1}_{r2}_{c}", [v1, v2])
                        
                        tup = []
                        for a in v1.domain():
                              for b in v2.domain():
                                    if a == b:
                                          continue
                                    else:
                                          tup.append((a,b))
                              
                        con.add_satisfying_tuples(tup)
                        csp.add_constraint(con)  
                      
    # All specified inequality constraints 
    for i in range(n):
          for j in range(1, 2*n-1, 2):
                if grid[i][j] in ['<', '>']:
                        left = variables[i][(j-1)//2]
                        right = variables[i][(j+1)//2]
                        
                        con = Constraint(f"Ineq_{i}_{j}", [left, right])
                        
                        if grid[i][j] == '<':
                              tup = [(a, b) for a in left.domain() for b in right.domain() if a < b]
                        elif grid[i][j] == '>':
                              tup = [(a, b) for a in left.domain() for b in right.domain() if a > b]
                        
                        con.add_satisfying_tuples(tup)
                        csp.add_constraint(con)
                        
                        
    return csp, variables

from itertools import product
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
      l = len(grid)
      variables = []
      var_list = []     #for object CSP to use
      #check all-diff() in row
      for i in range(l):
            
            row_var = []
          
            for j in range(0, 2*l-1, 2):
                  if grid[i][j] == 0:
                        domain = list(range(1,l+1))  
                  else:
                        domain = [grid[i][j]]   
                  
                  var = Variable(f"V{i}{j//2}", domain)     #create variables
            
                  #add variables into list variables
                  var_list.append(var)
                  #seperate variables in lists row by row for creating a 2D lists
                  row_var.append(var)
            
            #add variables into a 2D list
            variables.append(row_var)
      
      #building the csp problem
      csp = CSP("futoshiki_csp_model_2", var_list)
      
      # All-row different
      for r in range(l):
            scope = variables[r] #extract entire row from variables
            con = Constraint(f"Row_{r}", scope)
            
            satisfying_tuple = []
            
            domains = [var.domain() for var in scope]
            
            for values in product(*domains): # generates all combinations in domains
                   if len(set(values)) == len(values):  # all distinct, use set to remove dulplicates
                        satisfying_tuple.append(values)
            
            con.add_satisfying_tuples(satisfying_tuple)
            csp.add_constraint(con)
            
      #all - coloumn different
      for c in range(l):
            scope = [variables[r][c] for r in range(l)]
            con = Constraint(f"Col_{c}", scope)
            
            satisfying_tuple = []
            
            domains_col = [var.domain() for var in scope]
            
            for values in product(*domains_col):
                  if(len(set(values))) == len(values):
                        satisfying_tuple.append(values)
                        
            con.add_satisfying_tuples(satisfying_tuple)
            csp.add_constraint(con)
      
      # All specified inequality constraints 
      for i in range(l):
            for j in range(1, 2*l-1, 2):
                  if grid[i][j] in ['<', '>']:
                              left = variables[i][(j-1)//2]
                              right = variables[i][(j+1)//2]
                              
                              con = Constraint(f"Ineq_{i}_{j}", [left, right])
                              
                              if grid[i][j] == '<':
                                    tup = [(a, b) for a in left.domain() for b in right.domain() if a < b]
                              elif grid[i][j] == '>':
                                    tup = [(a, b) for a in left.domain() for b in right.domain() if a > b]
                              elif grid[i][j] == '.':
                                    continue
                              
                              con.add_satisfying_tuples(tup)
                              csp.add_constraint(con)
                              
                              
      return csp, variables