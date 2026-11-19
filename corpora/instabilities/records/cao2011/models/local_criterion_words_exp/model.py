# The local criterion eps_A = eps_W (see local_criterion_words) for the exponential imperfection of
# Eq. 5.1 (Fig. 9 draws eps_W = 0.456 beside its eps_A points); xi is the sweep variable only.


def run(inputs, settings):
    return {"eps_A": inputs["eps_W"]}
