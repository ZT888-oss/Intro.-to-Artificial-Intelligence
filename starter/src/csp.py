from .csp_variable import Variable
from .csp_constraint import Constraint

class CSP:
    """
    A constraint satisfaction problem, composed of variables and constraints.
    Variables can be defined during or after initialization, whereas
    constraints can only be added after initialization
    """

    def __init__(self, name: str, variables: list['Variable'] = []):
        """
        :param name: name of the CSP problem
        :param variables: list of variables to add to the CSP problem
        """

        self.name = name
        self.variables = []
        self.constraints = []
        self.vars_to_cons = dict()
        for v in variables:
            self.add_var(v)

    def add_var(self, variable):
        """
        Add variable to the list of variables and to the mapping of
        variables to constraints, both defined in self.
        """
        if not type(variable) is Variable:
            print(f"ERROR: cannot add object {variable} with type {type(variable)} to CSP object")
        elif variable in self.vars_to_cons:
            print(f"ERROR: variable {variable} already exists in CSP object")
        else:
            self.variables.append(variable)
            self.vars_to_cons[variable] = []

    def add_constraint(self, constraint: 'Constraint'):
        # TODO: Can you please verify this logic?
        # The docstring isn't clear. If there every variable
        # in the constraint's scope is in the CSP except for the last,
        # then we will have added this constraint to the mapping for
        # all of those variables and upon seeing the last variable,
        # we will return from this method before adding it to this CSP's
        # list of constraints.
        #
        # Is this correct behavior? This docstring
        # suggests that *every* variable needs to be present in this CSP for
        # the constraint to be valid for this CSP. Example:
        #
        # self.variables = [a, b]
        # constraint.name = 'f'
        # constraint.scope = [a, c]
        #
        # results in:
        #
        # self.vars_to_cons = {a: constraint named 'f'}
        # self.constraints = []
        """
        Add constraint to CSP. Note that all variables in the
        constraints scope must already have been added to the CSP.
        """
        if type(constraint) is not Constraint:
            print(f"ERROR: constraint {constraint} cannot be added to CSP")
        else:
            for variable in constraint.scope:
                if variable not in self.vars_to_cons:
                    print(f"ERROR: constraint {constraint} has unknown variable {variable}")
                    return
                self.vars_to_cons[variable].append(constraint)
            self.constraints.append(constraint)

    def get_all_cons(self) -> list['Constraint']:
        """
        Return the list of all constraints.
        """
        return self.constraints

    def get_cons_with_var(self, variable) -> list['Constraint']:
        """
        Return the list of constraints that include variable in their scope.
        """
        return list(self.vars_to_cons[variable])

    def get_all_vars(self) -> list['Variable']:
        """
        Return the list of all variables.
        """
        return list(self.variables)

    def get_all_unasgn_vars(self) -> list['Variable']:
        """
        Return the list of unassigned variables.
        """
        return [v for v in self.variables if not v.is_assigned()]

    def print_all(self):
        print("CSP", self.name)
        print("   Variables = ", self.variables)
        print("   Constraints = ", self.cons)

    def print_soln(self):
        print("CSP", self.name, " Assignments = ")
        for v in self.variables:
            print(v, " = ", v.get_assigned_value(), "    ", end='')
        print("")
