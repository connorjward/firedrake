''' This benchmark recreates the libceed Bake-off Problems as detailed here:
https://ceed.exascaleproject.org/bps/
using Firedrake.
'''

from math import prod

from FIAT import ufc_simplex
from FIAT.quadrature import GaussLobattoLegendreQuadratureLineRule as GLL_qlr
from finat.point_set import GaussLobattoLegendrePointSet as GLL_ps
from finat.quadrature import QuadratureRule, TensorProductQuadratureRule
from firedrake import *
from firedrake.petsc import PETSc
from mpi4py import MPI

import numpy as np
import pytest

parprint = PETSc.Sys.Print

def gauss_lobatto_legendre_line_rule(degree):
    ''' Create the Gauss Lobatto Legendre quadrature rule for a given `degree`
    on an interval
    '''
    fiat_rule = GLL_qlr(ufc_simplex(1), degree + 1)
    points = GLL_ps(fiat_rule.get_points())
    weights = fiat_rule.get_weights()
    return QuadratureRule(points, weights)

def make_tensor_product_rule(rule, dimension, degree):
    ''' Creates a tensor product quadrature rule from an interval quadrature
    rule for a given `dimension` and `degree`
    '''
    result = rule(degree)
    for _ in range(1, dimension):
        line_rule = rule(degree)
        result = TensorProductQuadratureRule([result, line_rule])
    return result

def setup_problem(problem_number, size, degree, tets=False):
    ''' Setup one of the bake-off problems in the range 1-6 (`problem_number`)
    Odd numbered problem_number are scalar fields
    Even numbered problem_number are vector fields
    1, 2 are mass matrix solves
    3-6  are Poisson solves
    5, 6 utilise under-integration using a GLL quadrature rule

    The problem `size` is s in the problem specification
    The problem `degree` is p in the problem specification

    Details available: https://ceed.exascaleproject.org/bps/

    Comments in the code below are derived from quoting this webpage
    '''

    # Consider meshes with E = 2**s (s = size) elements
    # That is a (2**s[1]) * (2**s[2]) * (2**s[3]) Cartesian mesh
    # with floor(s/3) <= s[3] <= s[2] <= s[1] <= floor(s/3) + 1
    # and s[1] + s[2] + s[3] = s
    # In the code s is represented by N
    q, r = divmod(size, 3)
    N = [2**(q + 1) if ii < r else 2**q for ii in range(3)]

    if tets:
        # Tetrahedral elements are not considered by the bake-off problems
        # they are included for comparison
        mesh = UnitCubeMesh(*N)
        E = 6*prod(N)
    else:
        # Use a 3D box mesh with hexahedral elements
        base_mesh = UnitSquareMesh(N[0], N[1], quadrilateral=True)
        mesh = ExtrudedMesh(base_mesh, N[2])
        E = prod(N)
    # Output: Number of mesh elements
    parprint(f'Total elements : {E}')
    # Output: Polynomial degree
    parprint(f'Polynomial degree: {degree}')

    if problem_number % 2 == 1:
        # Odd numbered problems use a scalar function space
        V = FunctionSpace(mesh, 'CG', degree=degree)
    else:
        # Even numbered problems use a vector function space
        V = VectorFunctionSpace(mesh, 'CG', degree=degree)
    ndofs = V.dim()
    # Output: Total number of degrees of freedom
    parprint(f'Total DOFs : {ndofs}')

    u = TrialFunction(V)
    v = TestFunction(V)
    if problem_number in {1, 2}:
        # Problems 1 and 2 are mass solves
        a = inner(u, v)*dx
    elif problem_number in {3, 4}:
        # Problems 3 and 4 are Poisson solves
        # using Gauss Legendre (GL) quadrature (full integration)
        a = inner(grad(u), grad(v))*dx
    elif problem_number in {5, 6}:
        # Problems 5 and 6 are Poisson solves
        # using Gauss Lobatto Legendre (GLL) quadrature (under-integration)
        GLL_rule = make_tensor_product_rule(
            gauss_lobatto_legendre_line_rule,
            dimension=3,
            degree=degree
        )
        a = inner(grad(u), grad(v))*dx(rule=GLL_rule)

    # No specification is given for the RHS
    # a constant vector seems to be used in examples
    f = Function(V)
    f.assign(1.0)
    L = inner(f, v)*dx

    # Boundary conditions are either no essential BCs
    # or essential BCs on the whole boundary.
    bcs = DirichletBC(V, zero(), ("on_boundary",))

    u_h = Function(V)
    problem = LinearVariationalProblem(a, L, u_h, bcs=bcs)
    return problem


class KSPTimeMonitor(object):
    ''' A custom KSP monitor for timing iterations
    '''
    def __init__(self, solver=None, max_its=1000):
        if solver:
            solver.snes.ksp.setMonitor(self)
        self.clock = 0
        self.iteration_count = 0
        self.all_times = np.zeros(max_its + 1)

    def __call__(self, ksp, its, rnorm):
        ''' Print residual and time for each iteration
        '''
        tdiff = MPI.Wtime() - self.clock
        self.all_times[its] = tdiff
        parprint(f'|   {its:2d} | {rnorm:14.12e} | {tdiff:14.12e} |')
        self.iteration_count += 1
        self.clock = MPI.Wtime()

    def __enter__(self):
        ''' Table header
        '''
        parprint('| iter | rnorm              | time(s)            |')
        parprint('|------|--------------------|--------------------|')
        self.clock = MPI.Wtime()
        self.total = self.clock

    def __exit__(self,*exc):
        ''' Calculate total time over all iterations
        '''
        self.total = MPI.Wtime() - self.total
        # Output: Time per iteration = total CG time / number of CG iterations
        # > Time is measured as maximum over all MPI ranks;
        # > using MPI_Wtime() or other similar function
        parprint(f'Average time per iteration: {self.total/self.iteration_count}')
        # Output: [optional] Number of iterations to reach relative residual reduction of 1e-6
        parprint(f'Total number of iterations: {self.iteration_count}')


def solve_problem(problem, solver_parameters):
    ''' Solve `problem` using `solver_parameters`
    and wrap the solve using the custom KSP monitor
    '''
    solver = LinearVariationalSolver(problem, solver_parameters=solver_parameters)
    time_monitor = KSPTimeMonitor(solver, solver_parameters['ksp_max_it'])
    with time_monitor:
        solver.solve()

def solver_parameters():
    ''' Returns solver parameters suitable for problem
    '''
    # Use the conjugate gradients (CG) iterative method to solve the linear
    # system. Since we are interested in evaluating the performance of the
    # QA/PA operator representation (see Terminology and Notation),
    # we assume no preconditioning, or simple diagonal preconditioning.
    params = {
        'mat_type': 'matfree',
        'ksp_type': 'cg',
        "ksp_rtol": 1e-6,
        'ksp_max_it': 999,
        'ksp_norm_type': 'unpreconditioned',
        'ksp_view': None,
        'ksp_monitor_true_residual_': None,
        'ksp_converged_reason': None,
        'pc_type':  'none'
    }

    # Jacobi options:
    # pc_jacobi_type = diagonal,rowmax,rowsum
    # pc_jacobi_abs
    # pc_jacobi_fixdiag
    alternative = {'pc_type': 'jacobi', 'pc_jacobi_type': 'diagonal'}
    params.update(alternative)
    return params

@pytest.fixture
def solver_parameter_fixture():
    return solver_parameters()

# For each of the Bake-off problems 1-6
# For a given mesh size (chosen as to fill a desired machine)
# Use function space degree p=1,2,3,...,8, and optionally higher p
# @pytest.fixture(params=[(ii, 12, p) for ii in range(1, 7) for p in range(1, 9)])
@pytest.fixture(params=[(i, 15, 3) for i in range(1, 7)])
def problem(request):
    problem_number, size, degree = request.param
    return setup_problem(problem_number, size, degree)

def benchmark_solve(problem, solver_parameter_fixture, benchmark):
    benchmark(solve_problem, problem, solver_parameter_fixture)


if __name__ == '__main__':
    # Useful for running a single benchmark problem
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Bake-off problem benchmark for Firedrake')

    parser.add_argument('--problem', type=int, default=1)
    parser.add_argument('--size', type=int, default=18)
    parser.add_argument('--degree', type=int, default=1)

    args, unknown = parser.parse_known_args()

    # TODO: Output more MPI info
    comm = COMM_WORLD
    # Output: Total number of MPI ranks and number of MPI ranks per compute node.
    parprint(f'Total ranks : {comm.size}')

    lvp = setup_problem(args.problem, args.size, args.degree)
    solve_problem(lvp, solver_parameters=solver_parameters())
