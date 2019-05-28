import unittest

import sympy as sp
from sympy import symbols

import context
from source.equations import DifferentialEquation

class TestDifferentialEquation(unittest.TestCase):

    def test_expression_parsed_correctly(self):

        ode = DifferentialEquation('x', ['x', 'y'], 'x*sin(y)^2 - y^3')
        x, y = symbols('x, y')
        expected_expr = x * sp.sin(y)**2 - y**3
        self.assertEqual(expected_expr, ode.expr)
    
    def test_parameters_are_extracted_correctly(self):

        ode = DifferentialEquation('x', ['x', 'y'], 'ax + bcy')
        expected_params = set(symbols('a, b, c'))
        self.assertEqual(set(expected_params), set(ode.params))

        ode = DifferentialEquation('x', ['x'], 'eftx')
        expected_params = set(symbols('e, f'))
        self.assertEqual(set(expected_params), set(ode.params))
    
    def test_set_param(self):

        ode = DifferentialEquation('x', ['x', 'y'], 'ax + bcy')
        ode.set_param('a', 10)
        self.assertEqual(ode.param_values['a'], 10)

if __name__ == '__main__':
    unittest.main()