# Digitizer comparison: results

Errors are a fraction of the axis span (in decades on the log axis), averaged over the read positions.
Coverage is the share of true values inside the claimed 95% interval. Width is the mean interval width,
as a fraction of the axis. Spread is the mean difference between the two runs of the same method.

| Figure | Method | Mean error | Max error | Coverage | Width | Missing | Spread | Cost | Status |
|---|---|---|---|---|---|---|---|---|---|
| fig8_KL300 | hybrid | 0.51% | 1.00% | 81% | 1.54% | 0 | 0.07% | $0.85 | passed, passed |
| fig8_KL1e4 | hybrid | 0.58% | 1.44% | 92% | 2.20% | 0 | 0.17% | $0.83 | passed, passed |
| fig2b_p5 | hybrid | 0.49% | 0.74% | 100% | 2.28% | 0 | 0.99% | $0.73 | passed, passed |
| fig3a_N2 | hybrid | 0.64% | 0.90% | 100% | 3.69% | 0 | 0.04% | $0.70 | passed, passed |
| fig3a_N10 | hybrid | 0.32% | 0.42% | 100% | 1.17% | 0 | 0.65% | $0.79 | passed, passed |
| fig3d_stoch_N10 | hybrid | 0.28% | 0.56% | 100% | 1.58% | 0 | 0.39% | $0.71 | passed, passed |
| fig4a_N100 | hybrid | 0.17% | 0.29% | 100% | 1.34% | 0 | 0.09% | $0.63 | passed, passed |
| fig4b_g1 | hybrid | 0.71% | 1.55% | 64% | 2.11% | 0 | 0.12% | $0.80 | passed, passed |

## Totals

| Method | Mean error | Coverage | Width | Missing | Spread | Cost |
|---|---|---|---|---|---|---|
| hybrid | 0.46% | 92% | 1.99% | 0 | 0.31% | $6.04 |
