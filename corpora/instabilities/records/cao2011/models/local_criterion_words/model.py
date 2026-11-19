# The local criterion stated in words (Fig. 5 caption, p. 109): the imperfect half-space becomes
# unstable when the local compressive strain at the deepest point A attains the Biot wrinkling
# strain, eps_A = eps_W, whatever the imperfection amplitude (xi is the sweep variable only).


def run(inputs, settings):
    return {"eps_A": inputs["eps_W"]}
