# Digitizer comparison: results

Errors are a fraction of the axis span (in decades on the log axis), averaged over the read positions.
Coverage is the share of true values inside the claimed 95% interval. Width is the mean interval width,
as a fraction of the axis. Spread is the mean difference between the two runs of the same method.

| Figure | Method | Mean error | Max error | Coverage | Width | Missing | Spread | Cost | Status |
|---|---|---|---|---|---|---|---|---|---|
| fig8_KL300 | hybrid | 0.45% | 0.61% | 100% | 1.80% | 0 | 0.00% | $0.45 | passed, passed |
| fig8_KL300 | code | 0.47% | 1.22% | 100% | 2.73% | 0 | 0.11% | $0.64 | passed, passed |
| fig8_KL1e4 | hybrid | 0.43% | 0.81% | 100% | 2.35% | 0 | 0.18% | $0.53 | passed, passed |
| fig8_KL1e4 | code | 0.61% | 2.02% | 92% | 3.36% | 0 | 0.08% | $0.53 | passed, passed |
| fig2b_p5 | hybrid | 0.90% | 1.32% | 100% | 4.22% | 0 | 0.34% | $0.47 | passed, passed |
| fig2b_p5 | code | 0.23% | 0.49% | 100% | 3.60% | 0 | 0.45% | $0.65 | passed, passed |
| fig3a_N2 | hybrid | 0.62% | 1.54% | 100% | 6.22% | 0 | 0.64% | $0.43 | passed, passed |
| fig3a_N2 | code | 0.36% | 1.42% | 93% | 3.13% | 0 | 0.20% | $0.69 | passed, passed |
| fig3a_N10 | hybrid | 0.53% | 0.87% | 100% | 2.50% | 0 | 0.20% | $0.35 | passed, passed |
| fig3a_N10 | code | 0.05% | 0.09% | 100% | 1.06% | 0 | 0.05% | $0.72 | passed, passed |
| fig3d_stoch_N10 | hybrid | 1.46% | 4.92% | 75% | 2.76% | 0 | 0.20% | $0.43 | passed, passed |
| fig3d_stoch_N10 | code | 0.21% | 0.42% | 100% | 2.72% | 0 | 0.10% | $0.68 | passed, passed |
| fig4a_N100 | hybrid | 0.28% | 0.35% | 100% | 2.22% | 0 | 0.00% | $0.42 | passed, passed |
| fig4a_N100 | code | 0.02% | 0.07% | 100% | 1.67% | 0 | 0.03% | $0.75 | passed, passed |
| fig4b_g1 | hybrid | 0.10% | 0.25% | 100% | 3.64% | 0 | 0.00% | $0.40 | passed, passed |
| fig4b_g1 | code | 0.05% | 0.14% | 100% | 2.82% | 0 | 0.11% | $0.66 | passed, passed |

## Totals

| Method | Mean error | Coverage | Width | Missing | Spread | Cost |
|---|---|---|---|---|---|---|
| hybrid | 0.60% | 97% | 3.21% | 0 | 0.19% | $3.46 |
| code | 0.25% | 98% | 2.64% | 0 | 0.14% | $5.32 |
