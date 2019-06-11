import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from scipy.integrate import solve_ivp
from sympy.utilities.lambdify import lambdify
from sympy import symbols
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    split_symbols,
    implicit_multiplication,
    convert_xor,
)

# transformation functions that modify the equation parser
TRANSFORMATIONS = standard_transformations + (
    split_symbols,              # used for implicit multiplication
    implicit_multiplication,    # makes multiplication operator (*) optional
    convert_xor,                # ^ used for exponentiation
)


class DifferentialEquation(object):
    """
    Handles first-order ODE's
    """
    def __init__(self, dep_var, phase_coords, expr_string):
        # dep_var is converted from a string into the corresponding Sympy symbol
        self.dep_var = symbols(dep_var)

        # indep_var is the t in dx/dt = f(x, t). For now it will be set to "t" for time
        self.indep_var = symbols('t')

        # phase_coords is an iterable of the degrees of freedom of the system.
        # It is passed as an iterable of single-char strings
        self.phase_coords = tuple(symbols(phase_coords))

        # expr is the Sympy expression representing the RHS of the ODE.
        self.expr = parse_expr(expr_string, transformations=TRANSFORMATIONS)

        # params are the symbols in the expression less the independent variable and the phase coordinates
        self.params = [
            s for s in self.expr.free_symbols
            if s not in (self.phase_coords + (self.indep_var,))
        ]
        
        # param_values maps a parameter string to its numerical value.
        # It is used when the ODE is evaluated as a function.
        # Each parameter in param_values must be set before the ODE expression
        # can be numerically evaluated.
        self.param_values = dict.fromkeys([str(p) for p in self.params])

        # func is the mathematical function generated from self.expr.
        # It is used to numerically solve the equation.
        self.func = lambdify([self.indep_var, self.phase_coords, *self.params], self.expr)
    
    def set_param(self, param, value):
        """
        Sets self.param_values[param] to value.
        If 
        """
        if param in self.param_values:
            self.param_values[param] = value
    
    def eval_rhs(self, t, r):
        # the r argument is expected to be a vector, so scalars are first packed into a list
        if np.isscalar(r):
            r = [r]
        return self.func(t, r, **self.param_values)
    
    def __str__(self): # implemented for readable printing of equation
        return "d{}/dt = {}".format(self.dep_var, self.expr)


class SystemOfEquations(object):
    """
    System of ODE's. Handles solving and evaluating the ODE's.
    """
    def __init__(self, system_coords, ode_expr_strings, params=None):
        # ode_expr_strings is a dictionary that maps the dependent variable 
        # of the equation (e.g. x in dx/dt = f(x,t)) to the corresponding
        # differential equation.
        self.ode_expr_strings = ode_expr_strings
        self.system_coords = system_coords
        self.dims = len(self.system_coords)

        # generate the list of expressions representing the system.
        # The elements in system_coords and ode_expr_strings are assumed
        # to correspond to each other in the order given.
        # i.e. system_coords[i] pairs with ode_expr_strings[i]
        self.equations = []
        for i in range(len(system_coords)):
            coord = system_coords[i]
            expr = ode_expr_strings[i]
            self.equations.append(DifferentialEquation(coord, system_coords, expr))

        self.var_function_pairs = {}
        for var, eqn in zip(self.system_coords, self.equations):
            self.var_function_pairs[var] = eqn
        
        # Set the parameters in the ODEs
        self.params = params
        for p, val in params.items():
            for eqn in self.equations:
                eqn.set_param(p, val)
    
    def __str__(self):
        s = ["{}".format(self.__repr__())]
        for eqn in self.equations:
            s.append("{}".format(eqn))
        return "\n".join(s)
    
    def solve(self, t_span, r0, method="LSODA"):
        def functions(t, r):
            return tuple(eqn.eval_rhs(t, r) for eqn in self.equations)    
        return solve_ivp(functions, t_span, r0, method="RK45", max_step=0.02)

    def phasespace_eval(self, phase_coords, r):
        """
        Allows for the phase space to be evaluated using the SOE class.
        
        Example:
        >>> import numpy as np
        >>> from equations import SystemOfEquations
        >>> sys = SystemOfEquations(phase_coords, eqns, params=params)
        >>> X, Y = np.meshgrid(np.arange(-10, 10, 1), np.arange(-10, 10, 1))
        >>> U, V = sys.phasespace_eval(t=None, r=np.array([X,Y]))

        Added by Mikie on 29/05/2019
        """
        for p in phase_coords:
            if not (p in self.system_coords): return

        phase_list = tuple(self.var_function_pairs[p] for p in phase_coords)
        return tuple(eqn.eval_rhs(t=None, r=r) for eqn in phase_list)


def example():
    # 2-D
    system_coords = ['x', 'y']
    eqns = [
        'ax + by',
        'cx + dy'
    ]
    params = {'a': -1, 'b': 5, 'c': -4, 'd': -2}
    r0 = [0.4, -0.3]
    t = np.linspace(0, 40, 5000)

    sys = SystemOfEquations(system_coords, eqns, params=params)
    print(sys)
    sol = sys.solve(t, r0)
    plt.plot(sol[:,0], sol[:,1])
    plt.show()

if __name__ == "__main__":
    example()