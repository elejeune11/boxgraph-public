# Table S1 caption (SI p. 3): F ∝ rb^3 d^-4, so at the fixed reference distance d0 the fitted F0 ∝ rb^3.
# Printed with "∝": prefactor 1 (the build fits the one constant). rb in mm; F0 in N.


def run(inputs, settings):
    return {"F0": inputs["rb"] ** 3}
