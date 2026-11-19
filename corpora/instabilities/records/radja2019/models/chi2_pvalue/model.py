# Upper tail of the chi-square distribution: the paper states the test (statistic and
# degrees of freedom) and its p values; the chi-square reference distribution is the usual one.
from scipy.stats import chi2


def run(inputs, settings):
    return {"p": float(chi2.sf(inputs["LR"], round(inputs["dof"])))}
