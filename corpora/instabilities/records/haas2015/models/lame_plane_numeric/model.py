# Minimize the plane-sheet energy (2.5) over piecewise-linear r(s) on [0, s_max]:
#   E = int s { a^2 + b^2 + 2 nu a b } ds,  a = r' - f(s),  b = r/s - f(s),
#   f(s) = f for s < 1 and 1 for s > 1; r(0) = 0, r(s_max) = s_max.
# E is quadratic in the nodal values, so the minimum solves one sparse linear system.
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


def run(inputs, settings):
    nu, f = inputs["nu"], inputs["f"]
    n = int(settings["n"])
    s_max = float(settings["s_max"])
    m = int(round(n * s_max))          # elements; s = 1 is a node
    s = np.linspace(0.0, s_max, m + 1)
    i1 = n                              # node at s = 1
    gp = np.array([0.5 - 0.5 / np.sqrt(3.0), 0.5 + 0.5 / np.sqrt(3.0)])
    rows, cols, vals = [], [], []
    g = np.zeros(m + 1)
    for e in range(m):
        s0, s1 = s[e], s[e + 1]
        h = s1 - s0
        fe = f if s1 <= 1.0 + 1e-12 else 1.0
        for t in gp:
            sq = s0 + t * h
            w = 0.5 * h * sq            # Gauss weight times the factor s
            Ba = np.array([-1.0 / h, 1.0 / h])
            Bb = np.array([1.0 - t, t]) / sq
            H = 2.0 * (np.outer(Ba, Ba) + np.outer(Bb, Bb) + nu * (np.outer(Ba, Bb) + np.outer(Bb, Ba)))
            # linear part from the -f terms: d/dr of [-2 f (a + b) (1 + nu)] style terms
            lin = -2.0 * fe * ((1.0 + nu) * Ba + (1.0 + nu) * Bb)
            idx = [e, e + 1]
            for p in range(2):
                g[idx[p]] += w * lin[p]
                for q in range(2):
                    rows.append(idx[p])
                    cols.append(idx[q])
                    vals.append(w * H[p, q])
    K = coo_matrix((vals, (rows, cols)), shape=(m + 1, m + 1)).tocsr()
    # Dirichlet: r(0) = 0, r(s_max) = s_max
    fixed = {0: 0.0, m: s_max}
    free = np.array([i for i in range(m + 1) if i not in fixed])
    rhs = -g[free]
    for j, v in fixed.items():
        rhs -= K[free, :][:, [j]].toarray().ravel() * v
    r = np.zeros(m + 1)
    for j, v in fixed.items():
        r[j] = v
    r[free] = spsolve(K[free, :][:, free].tocsc(), rhs)
    return {"Phi": float(r[i1])}
