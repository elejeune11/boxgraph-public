# Two-sided paired t-test between load 1 and another load over the nine dogs (Table 1 legend).
from scipy import stats

N = 9


def run(inputs, settings):
    a = [inputs[f"a{i}"] for i in range(1, N + 1)]
    b = [inputs[f"b{i}"] for i in range(1, N + 1)]
    return {"p": float(stats.ttest_rel(a, b).pvalue)}
