# Leading-order pure-invagination problem (B 14): b0'''' + b0 = K (delta''(xi + L/2) - delta''(xi - L/2))
# on the whole line, with decay at infinity. It is solved on a periodic grid of n_points over
# [-x_half, x_half) by FFT (the decaying Green function has Fourier transform 1/(k^4 + 1)).
# (B 11), int b0 = 0, then holds by symmetry; the first of (B 12), int b0^2 = 2 sin(Theta), fixes K:
# K^2 / sin(Theta) = 2 / int u^2, u = b0 / K. Output: K / sqrt(sin Theta).
import numpy as np


def run(inputs, settings):
    L = inputs["L"]
    X = float(settings["x_half"])
    N = int(settings["n_points"])
    dx = 2.0 * X / N
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    # Fourier transform of delta''(xi + L/2) - delta''(xi - L/2) is -k^2 (e^{ikL/2} - e^{-ikL/2})
    uh = -(k ** 2) * (2j * np.sin(k * L / 2.0)) / (k ** 4 + 1.0)
    # Parseval on the grid: int u^2 dxi = (1/2pi) int |uh|^2 dk ~ sum |uh|^2 dk / (2 pi)
    dk = 2.0 * np.pi / (N * dx)
    I = float(np.sum(np.abs(uh) ** 2) * dk / (2.0 * np.pi))
    return {"Ks": float(np.sqrt(2.0 / I))}
