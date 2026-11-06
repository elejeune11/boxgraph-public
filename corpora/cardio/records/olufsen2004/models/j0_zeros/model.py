from scipy.special import jn_zeros


def run(inputs, settings):
    b = jn_zeros(0, 3)
    return {"beta1": float(b[0]), "beta2": float(b[1]), "beta3": float(b[2])}
