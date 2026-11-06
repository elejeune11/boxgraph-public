# Eq. 15: C_Ti proportional to the area compliance C_Ai of the terminal vessel at its distal end.
# C_A = D * A with D the segment's distensibility (Table 2) and A = pi d^2/4 at the distal diameter;
# the common factor C_T / sum(C_A) is eliminated by scaling from a reference bed.


def run(inputs, settings):
    ca = inputs["D"] * inputs["d"] ** 2
    ca_ref = inputs["D_ref"] * inputs["d_ref"] ** 2
    return {"CT": inputs["CT_ref"] * ca / ca_ref}


def symbolic():
    import sympy as sp
    CT_ref, D_ref, d_ref, D, d = sp.symbols("CT_ref D_ref d_ref D d", positive=True)
    return {"CT": CT_ref * D * d ** 2 / (D_ref * d_ref ** 2)}
