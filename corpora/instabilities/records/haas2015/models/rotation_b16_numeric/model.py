# Second-order pure-invagination problem, solved by FFT on a periodic grid over [-x_half, x_half).
# From (B 8): sigma0'' = a0' = -b0 and sigma0 = b0'' + K0, K0 = K[delta(xi + L/2) - delta(xi - L/2)],
# so b0'''' + b0 = -K0'' and sigma0 = K[G(xi + L/2) - G(xi - L/2)], b0 = -K[G''(xi + L/2) - G''(xi - L/2)],
# where G is the decaying Green function of d^4 + 1 (Fourier transform 1/(k^4 + 1)). K is fixed by
# int b0^2 = 2 sin(Theta) (B 12). Then (B 16): b1'''' + b1 = cot(Theta){(b0 sigma0)'' - b0^2 / 2}.
# The midpoint rotation is gamma^2 b1(0) = (d/delta) b1(0) since b0(0) = 0 (b0 is odd). The output is
# -b1(0) / cos(Theta), independent of Theta (the setting theta only sets the arithmetic).
import numpy as np


def run(inputs, settings):
    L = inputs["L"]
    X = float(settings["x_half"])
    N = int(settings["n_points"])
    th = float(settings["theta"])
    dx = 2.0 * X / N
    x = -X + dx * np.arange(N)
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    Gh = 1.0 / (k ** 4 + 1.0)
    # transform of g(xi + L/2) - g(xi - L/2), with xi measured on the grid from x[0]
    shift = np.exp(1j * k * L / 2.0) - np.exp(-1j * k * L / 2.0)
    phase0 = np.exp(1j * k * x[0])       # grid starts at x[0], not 0

    def to_real(fh):
        return np.real(np.fft.ifft(fh * phase0)) / dx

    sig_u = to_real(Gh * shift)                  # sigma0 / K
    b0_u = to_real(-(-(k ** 2)) * Gh * shift)    # b0 / K = -(G''(+) - G''(-))
    I = float(np.sum(b0_u ** 2) * dx)
    K = np.sqrt(2.0 * np.sin(th) / I)
    b0 = K * b0_u
    s0 = K * sig_u
    Fh = np.fft.fft(b0 * s0)
    Qh = np.fft.fft(0.5 * b0 ** 2)
    Rh = (np.cos(th) / np.sin(th)) * (-(k ** 2) * Fh - Qh)
    b1 = np.real(np.fft.ifft(Rh / (k ** 4 + 1.0)))
    i0 = int(np.argmin(np.abs(x)))
    return {"B": float(-b1[i0] / np.cos(th))}
