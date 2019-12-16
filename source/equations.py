import time

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from scipy.integrate import solve_ivp
from sympy.utilities.lambdify import lambdify
from sympy import symbols, Matrix
from sympy.matrices.dense import matrix2numpy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    split_symbols,
    implicit_multiplication,
    convert_xor,
)

# transformation functions that modify the equation parser
TRANSFORMATIONS = standard_transformations + (
    split_symbols,  # used for implicit multiplication
    implicit_multiplication,  # makes multiplication operator (*) optional
    convert_xor,  # ^ used for exponentiation
)


class DifferentialEquation:
    """
    Handles first-order ODE's
    """

    def __init__(self, dep_var, phase_coords, expr_string) -> None:
        # dep_var is converted from a string into the corresponding Sympy symbol
        self.dep_var = symbols(dep_var)

        # indep_var is the t in dx/dt = f(x, t). For now it will be set to "t" for time
        self.indep_var = symbols("t")

        # phase_coords is an iterable of the degrees of freedom of the system.
        # It is passed as an iterable of single-char strings
        self.phase_coords = tuple(symbols(phase_coords))

        # expr is the Sympy expression representing the RHS of the ODE.
        self.expr = parse_expr(expr_string, transformations=TRANSFORMATIONS)

        # params are the symbols in the expression less the independent variable and the phase coordinates
        self.params = [
            s
            for s in self.expr.free_symbols
            if s not in (self.phase_coords + (self.indep_var,))
        ]

        # param_values maps a parameter string to its numerical value.
        # It is used when the ODE is evaluated as a function.
        # Each parameter in param_values must be set before the ODE expression
        # can be numerically evaluated.
        self.param_values = dict.fromkeys([str(p) for p in self.params])

        # func is the mathematical function generated from self.expr.
        # It is used to numerically solve the equation.
        self.func = lambdify(
            [self.indep_var, self.phase_coords, *self.params], self.expr
        )

    def set_param(self, param, value) -> None:
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

    def __str__(self) -> str:  # implemented for readable printing of equation
        return f"d{self.dep_var}/dt = {self.expr}"


class SystemOfEquations:
    """
    System of ODE's. Handles solving and evaluating the ODE's.
    """

    def __init__(
        self, system_coords, ode_expr_strings, params=None, *args, **kwargs
    ) -> None:
        # ode_expr_strings is a dictionary that maps the dependent variable
        # of the equation (e.g. x in dx/dt = f(x,t)) to the corresponding
        # differential equation.
        self.ode_expr_strings = ode_expr_strings
        self.system_coords = system_coords
        self.system_coord_symbols = symbols(system_coords)
        self.dims = len(self.system_coords)

        # generate the list of expressions representing the system.
        # The elements in system_coords and ode_expr_strings are assumed
        # to correspond to each other in the order given.
        # i.e. system_coords[i] pairs with ode_expr_strings[i]
        self.equations = [
            DifferentialEquation(coord, system_coords, expr)
            for coord, expr in zip(system_coords, ode_expr_strings)
        ]

        # Set the parameters in the ODEs
        self.params = params
        for p, val in params.items():
            for eqn in self.equations:
                eqn.set_param(p, val)

        # Calculate the symbolic Jacobian of the system
        r = Matrix([equation.expr for equation in self.equations])
        self.jacobian = r.jacobian(self.system_coord_symbols)
        # print(f"Jacobian: {self.jac}")

        # calculated fixed points are cached here
        self.fixed_points = self.calc_fixed_points()

    def __str__(self) -> str:
        return f"{self.__repr__()}" + "\n".join(f"{eqn}" for eqn in self.equations)

    def solve(self, t_span, r0, method="LSODA"):
        return solve_ivp(self.phasespace_eval, t_span, r0, method=method, max_step=0.02)

    def phasespace_eval(self, t, r) -> tuple:
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
        return tuple(eqn.eval_rhs(t=t, r=r) for eqn in self.equations)

    def eval_jacobian(self, r):
        """
        Evaluates the symbolic Jacobian of the system at the point r
        """
        # The subs method substitutes one symbol or value for another
        jacobian = self.jacobian.subs(self.params)
        jacobian = jacobian.subs(list(zip(self.system_coord_symbols, r)))
        return jacobian

    def show_jacobian(self, eval=False, r=None):
        """
        Prints Jacobian. May be evaluated at a point first, or printed symbolically
        """

        jacobian = self.eval_jacobian(r) if eval else self.jacobian
        sp.pprint(jacobian)

    def eigenvects(self, r=None):
        """
        Calculates the eigenvalues and eigenvectors of the system's Jacobian.
        Return list of triples (eigenval, multiplicity, eigenspace).
        """

        jacobian = self.eval_jacobian(r) if r is not None else self.jacobian
        return jacobian.eigenvects(simplify=True)

    def calc_fixed_points(self):
        """
        Returns a set of fixed points as tuples.
        """

        eqns = [eqn.expr for eqn in self.equations]
        eqns = [eqn.subs(self.params) for eqn in eqns]
        fps = sp.solve(eqns, self.system_coord_symbols)
        
        fps_as_cmplx = {tuple(complex(z) for z in fp) for fp in fps}
        fps_rounded = {tuple(round_complex(z, 3) for z in fp) for fp in fps_as_cmplx}
        fps_no_cmplx = {
            fp for fp in fps_rounded if all(not abs(z.imag) > 0 for z in fp)
        }
        fps_real = {tuple(z.real for z in fp) for fp in fps_no_cmplx}

        return fps_real

    def find_fixed_point(self, r_init):
        """
        Returns the value of a fixed point based a Newton's method computation.
        See https://en.wikipedia.org/wiki/Newton%27s_method for details.
        """

        num_iter = 50
        r = r_init

        for _ in range(num_iter):
            J = self.eval_jacobian(r)
            J_inv = matrix2numpy(J.inv(), dtype="float")
            r = r - J_inv.dot(self.phasespace_eval(t=None, r=r))

        self.fixed_points.add(r)
        return r


def round_complex(x, n):
    return round(x.real, n) + round(x.imag, n) * 1j


def get_closest_point(point, other_points):

    closest_point = None
    closest_distance = None

    for pt in other_points:
        if closest_distance is None:
            closest_point = pt
            closest_distance = np.hypot(pt, point)
            continue

        distance = np.hypot(point, pt)
        if distance < closest_distance:
            closest_point = pt
            closest_distance = distance

    return closest_point


def example():
    # 2-D
    system_coords = ["x", "y"]
    # eqns = ["ax + by", "cx + dy"]
    eqns = ["2x - y + 3(x^2-y^2) + 2xy", "x - 3y - 3(x^2-y^2) + 3xy"]
    params = {"a": -1, "b": 5, "c": -4, "d": -2}
    r0 = [0.4, -0.3]
    t_span = (0, 40)

    sys = SystemOfEquations(system_coords, eqns, params=params)
    print(sys)

    # r = [0.5, 0.5]
    r = [-1, -1]
    print(f"Jacobian evaluated at {r}:")
    sys.show_jacobian(eval=True, r=r)

    print(f"finding fixed point from initial guess {r}...")
    fp = sys.find_fixed_point(r)
    print(f"fixed point: {fp}")
    fp_jac = sys.eval_jacobian(fp)
    sp.pprint(fp_jac)
    sp.pprint(fp_jac.trace())
    sp.pprint(fp_jac.det())

    print("\nFixed points:\n")
    print(sys.calc_fixed_points())

    # Calculate eigenvalues and eigenvectors
    sp.pprint(sys.eigenvects(r))

    sol = sys.solve(t_span, r0)
    print(sol)
    plt.plot(sol.y[0], sol.y[1])
    plt.show()


if __name__ == "__main__":
    example()
