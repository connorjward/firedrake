from firedrake import *
import pytest


def gtmg_mixed_poisson():
    m = UnitCubeMesh(12, 12, 12)
    nlevels = 2
    mh = MeshHierarchy(m, nlevels)
    mesh = mh[-1]
    x = SpatialCoordinate(mesh)

    def get_p1_space():
        return FunctionSpace(mesh, "CG", 1)

    def get_p1_prb_bcs():
        return DirichletBC(get_p1_space(), Constant(0.0), "on_boundary")

    def p1_callback():
        P1 = get_p1_space()
        p = TrialFunction(P1)
        q = TestFunction(P1)
        return inner(grad(p), grad(q))*dx

    degree = 1
    RT = FunctionSpace(mesh, "RT", degree)
    DG = FunctionSpace(mesh, "DG", degree - 1)
    W = RT * DG

    sigma, u = TrialFunctions(W)
    tau, v = TestFunctions(W)

    f = Function(DG)
    f.interpolate(
        + 2*(x[1] - 1)*x[1]*(x[2] - 1)*x[2]
        + 2*(x[0] - 1)*x[0]*(x[2] - 1)*x[2]
        + 2*(x[0] - 1)*x[0]*(x[1] - 1)*x[1]
    )

    a = (inner(sigma, tau) - inner(u, div(tau)) + inner(div(sigma), v))*dx
    L = inner(f, v)*dx

    w = Function(W)
    params = {'mat_type': 'matfree',
              'ksp_type': 'preonly',
              'pc_type': 'python',
              'pc_python_type': 'firedrake.HybridizationPC',
              'hybridization': {'ksp_type': 'cg',
                                'mat_type': 'matfree',
                                'pc_type': 'python',
                                'pc_python_type': 'firedrake.GTMGPC',
                                'gt': {'mg_levels': {'ksp_type': 'chebyshev',
                                                     'pc_type': 'jacobi',
                                                     'ksp_max_it': 3},
                                       'mg_coarse': {'ksp_type': 'preonly',
                                                     'pc_type': 'mg',
                                                     'pc_mg_type': 'full',
                                                     'mg_levels': {'ksp_type': 'chebyshev',
                                                                   'pc_type': 'jacobi',
                                                                   'ksp_max_it': 3}}}}}
    appctx = {'get_coarse_operator': p1_callback,
              'get_coarse_space': get_p1_space,
              'coarse_space_bcs': get_p1_prb_bcs()}

    solve(a == L, w, solver_parameters=params, appctx=appctx)
    _, uh = w.split()

    # Analytical solution
    f.interpolate(x[0]*(1 - x[0]) * x[1]*(1 - x[1]) * x[2]*(1 - x[2]))

    assert errornorm(f, uh, norm_type="L2") < 1e-5
    return errornorm(f, uh, norm_type="L2")


def benchmark_hybridisation_gtmg(benchmark):
    err = benchmark(gtmg_mixed_poisson)


if __name__ == '__main__':
    gtmg_mixed_poisson()
