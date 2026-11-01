# Digitizer comparison: results

Errors are a fraction of the axis span (in decades on the log axis), averaged over the read positions.
Coverage is the share of true values inside the claimed 95% interval. Width is the mean interval width,
as a fraction of the axis. Spread is the mean difference between the two runs of the same method.

| Figure | Method | Mean error | Max error | Coverage | Width | Missing | Spread | Cost | Status |
|---|---|---|---|---|---|---|---|---|---|
| single | hybrid | 0.02% | 0.05% | 100% | 0.79% | 0 | 0.00% | $0.49 | passed, passed |
| single | eye | 0.17% | 0.50% | 100% | 6.17% | 0 | 0.03% | $0.29 | passed, passed |
| single | code | 0.02% | 0.09% | 100% | 2.59% | 0 | 0.02% | $0.37 | passed, passed |
| log | hybrid | 0.01% | 0.04% | 100% | 0.55% | 0 | 0.00% | $0.52 | passed, passed |
| log | eye | 0.01% | 0.04% | 100% | 1.96% | 0 | 0.01% | $0.30 | passed, passed |
| log | code | 0.01% | 0.01% | 100% | 1.03% | 0 | 0.01% | $0.36 | passed, passed |
| family | hybrid | 0.02% | 0.03% | 100% | 0.48% | 0 | 0.00% | $0.51 | passed, passed |
| family | eye | 0.06% | 0.11% | 100% | 1.60% | 0 | 0.08% | $0.78 | passed, passed |
| family | code | 0.02% | 0.03% | 100% | 4.34% | 0 | 0.00% | $0.29 | passed, passed |
| crossing | hybrid | 0.02% | 0.03% | 100% | 0.52% | 0 | 0.00% | $1.05 | passed, passed |
| crossing | eye | 0.08% | 0.35% | 100% | 2.68% | 0 | 0.14% | $0.56 | passed, passed |
| crossing | code | 0.28% | 0.47% | 100% | 3.70% | 0 | 0.06% | $0.30 | passed, passed |
| scan | hybrid | 0.71% | 2.53% | 42% | 1.07% | 0 | 0.83% | $0.96 | passed, passed |
| scan | eye | 0.69% | 2.30% | 100% | 3.90% | 0 | 0.85% | $0.86 | passed, passed |
| scan | code | 1.32% | 4.50% | 100% | 9.46% | 0 | 1.03% | $0.34 | passed, passed |
| markers | hybrid | 0.00% | 0.01% | 100% | 0.17% | 0 | 0.00% | $0.51 | passed, passed |
| markers | eye | 0.08% | 0.10% | 100% | 2.30% | 0 | 0.04% | $0.32 | passed, passed |
| markers | code | 0.04% | 0.10% | 100% | 1.35% | 0 | 0.07% | $0.41 | passed, passed |

## Totals

| Method | Mean error | Coverage | Width | Missing | Spread | Cost |
|---|---|---|---|---|---|---|
| hybrid | 0.13% | 90% | 0.60% | 0 | 0.14% | $4.04 |
| eye | 0.18% | 100% | 3.10% | 0 | 0.19% | $3.12 |
| code | 0.28% | 100% | 3.75% | 0 | 0.20% | $2.07 |
