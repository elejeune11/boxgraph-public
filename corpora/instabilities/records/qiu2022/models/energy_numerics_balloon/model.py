# Numerical minimization of the energy functional Eq. 2 over the rotation function phi(mu) of Eq. 5
# and the axial strain change de0, at an imposed curvature, in the balloon normalization (Eq. 4).
# Eq. 2 divided by S_z R, with x, y in units of R and alpha^2 = D_theta/(S_z R^2):
#   Phi = 1/2 int [alpha^2 (phi')^2 + (e0 + k y)^2] dmu + p pi [1 + e0 + k/(2 pi) int y dmu]
#         - p int x (1 + e0 + k y) sin(mu + phi) dmu
# with x(mu) = int_0^mu cos(mu' + phi), y(mu) = int_0^mu sin(mu' + phi), phi = sum_n a_n sin(n mu)
# and the closure 0 = int_0^2pi cos(mu + phi) dmu (Eq. 5). Phi is quadratic in e0, so e0 is
# eliminated exactly. The torque is M = dPhi/dk at the minimum (envelope theorem, p. 3).
import numpy as np
from scipy.optimize import minimize


def _integrate(f, mu):
    """Periodic antiderivative with F(0) = 0 of samples f on a uniform periodic grid, spectrally."""
    n = len(f)
    c = np.fft.rfft(f)
    mean = c[0].real / n
    k = np.arange(len(c))
    g = np.zeros_like(c)
    g[1:] = c[1:] / (1j * k[1:])
    F = np.fft.irfft(g, n)
    return mean * mu + F - F[0]


class Problem:
    def __init__(self, k, p, alpha, n_modes, n_grid):
        self.k, self.p, self.alpha = k, p, alpha
        self.mu = 2 * np.pi * np.arange(n_grid) / n_grid
        self.n = np.arange(1, n_modes + 1)
        self.S = np.sin(np.outer(self.n, self.mu))  # modes x grid
        self.C = np.cos(np.outer(self.n, self.mu)) * self.n[:, None]
        self.w = 2 * np.pi / n_grid

    def shape(self, a):
        phi = a @ self.S
        dphi = a @ self.C
        c, s = np.cos(self.mu + phi), np.sin(self.mu + phi)
        x = _integrate(c, self.mu)
        y = _integrate(s, self.mu)
        return phi, dphi, c, s, x, y

    def parts(self, a):
        k, p, al, w = self.k, self.p, self.alpha, self.w
        phi, dphi, c, s, x, y = self.shape(a)
        area = w * np.sum(x * s)
        ybar = w * np.sum(y) / (2 * np.pi)
        e0 = -k * ybar - p * (np.pi - area) / (2 * np.pi)
        strain = e0 + k * y
        energy = (0.5 * w * np.sum(al**2 * dphi**2 + strain**2)
                  + p * np.pi * (1 + e0 + k * ybar) - p * w * np.sum(x * (1 + strain) * s))
        torque = w * np.sum(strain * y) + p * np.pi * ybar - p * w * np.sum(x * y * s)
        return dict(phi=phi, dphi=dphi, x=x, y=y, e0=e0, strain=strain, energy=energy, torque=torque)

    def closure(self, a):
        _, _, c, _, _, _ = self.shape(a)
        return self.w * np.sum(c)

    def solve(self, a0=None):
        scale = max(self.k**2, 1e-30)
        a0 = np.zeros(len(self.n)) if a0 is None else a0
        if a0 is None or not np.any(a0):
            a0 = a0.copy()
            if len(a0) >= 2:  # start from the Eq. 7 ansatz, a2 = -k^2 / 8(alpha^2 + p/3)
                a0[1] = -self.k**2 / (8 * (self.alpha**2 + self.p / 3))
                a0[1] = max(a0[1], -0.6)
        res = minimize(lambda a: self.parts(a)["energy"] / scale, a0, method="SLSQP",
                       constraints=[{"type": "eq", "fun": self.closure}],
                       options={"ftol": 1e-14, "maxiter": 500})
        return res.x, self.parts(res.x)


def settings_of(settings):
    return int(settings.get("n_modes", 12)), int(settings.get("n_grid", 256))


def run(inputs, settings):
    n_modes, n_grid = settings_of(settings)
    pr = Problem(inputs["khat"], inputs["phat"], inputs["alpha"], n_modes, n_grid)
    _, sol = pr.solve()
    return {"Mhat": float(sol["torque"])}
