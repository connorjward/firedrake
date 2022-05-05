import numpy as np
import pytest

from firedrake import *
from firedrake.petsc import PETSc


parprint = PETSc.Sys.Print


def run_solve(problem, parameters):
    solver = LinearVariationalSolver(problem, solver_parameters=parameters)
    return solver.solve()


@pytest.fixture(scope="module")
def mesh():
    Nx = 8
    Nref = 3

    # Create mesh and mesh hierarchy
    mesh = UnitCubeMesh(Nx, Nx, Nx)
    hierarchy = MeshHierarchy(mesh, Nref)
    return hierarchy[-1]


@pytest.fixture
def V(mesh):
    degree = 2
    return FunctionSpace(mesh, "CG", degree)


@pytest.fixture
def a():
    return Constant(1)


@pytest.fixture
def b():
    return Constant(2)


@pytest.fixture
def coords(mesh):
    return SpatialCoordinate(mesh)


@pytest.fixture
def truth(V, a, b, coords):
    x, y, z = coords
    exact = sin(pi*x)*tan(pi*x/4)*sin(a*pi*y)*sin(b*pi*z)
    return Function(V).interpolate(exact)


@pytest.fixture
def problem(mesh, V, a, b, coords):
    u = TrialFunction(V)
    v = TestFunction(V)

    bcs = DirichletBC(V, zero(), ("on_boundary",))

    x, y, z = coords

    f = -pi**2 / 2
    f *= 2*cos(pi*x) - cos(pi*x/2) - 2*(a**2 + b**2)*sin(pi*x)*tan(pi*x/4)
    f *= sin(a*pi*y)*sin(b*pi*z)

    # Define the problem using the bilinear form `a` and linear functional `L`
    a = dot(grad(u), grad(v))*dx
    L = f*v*dx
    u_h = Function(V)
    u_h.assign(0)
    return LinearVariationalProblem(a, L, u_h, bcs=bcs)


# TODO Do we want to benchmark all of these?
# @pytest.fixture(params=["lu_mumps", "cg_amg", "cg_gmg_v", "fmg", "fmg_matfree_telescope"])
@pytest.fixture(params=["fmg_matfree_telescope"])
def solver_parameters(request):
    parameters = {
        # Direct solve with LU
        "lu_mumps": {
            "snes_view": None,
            "ksp_type": "preonly",
            "pc_type": "lu",
            "pc_factor_mat_solver_type": "mumps"
        },

        # Conjugate Gradient (CG) with Algebraic Multigrid (AMG)
        "cg_amg": {
            "snes_view": None,
            "ksp_type": "cg",
            "pc_type": "gamg",
            "pc_mg_log": None
        },

        # CG with Geometric Multigrid (GMG) V-cycles
        "cg_gmg_v": {
            "snes_view": None,
            "ksp_type": "cg",
            "pc_type": "mg",
            "pc_mg_log": None
        },

        # CG + GMG F-cycles
        "fmg": {
            "snes_view": None,
            "ksp_type": "cg",
            "pc_type": "mg",
            "pc_mg_log": None,
            "pc_mg_type": "full",
            "mg_levels_ksp_type": "chebyshev",
            "mg_levels_ksp_max_it": 2,
            "mg_levels_pc_type": "jacobi",
            "mg_coarse_pc_type": "lu",
            "mg_coarse_pc_factor_mat_solver_type": "mumps"
        },

        # CG + GMG F-cycles and telescoping
        "fmg_matfree_telescope": {
            "snes_view": None,
            "mat_type": "matfree",
            "ksp_type": "cg",
            "pc_type": "mg",
            "pc_mg_log": None,
            "pc_mg_type": "full",
            "mg_levels_ksp_type": "chebyshev",
            "mg_levels_ksp_max_it": 2,
            "mg_levels_pc_type": "jacobi",
            "mg_coarse_pc_type": "python",
            "mg_coarse_pc_python_type": "firedrake.AssembledPC",
            "mg_coarse_assembled": {
                "mat_type": "aij",
                "pc_type": "telescope",
                "pc_telescope_reduction_factor": 1,  # set to number of nodes!
                "pc_telescope_subcomm_type": "contiguous",
                "telescope_pc_type": "lu",
                "telescope_pc_factor_mat_solver_type": "mumps"
            }
        }
    }
    return parameters[request.param]


def benchmark_solve(problem, solver_parameters, truth, benchmark):
    sol = benchmark(run_solve, problem, solver_parameters)
    # TODO What is a reasonable tolerance here?
    # assert np.isclose(errornorm(truth, sol), 0)
