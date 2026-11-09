# Exploratory results - 2026-11-09

**Status:** initial feasibility; the requested matched semigrokking-vs-gradual causal contrast is NOT yet established.

## Trained networks

| Model | First fit>=99% | First test>=55% | Final test | Eligible 55-65% plateau |
|---|---:|---:|---:|---|
| mlp_p31_h300_frac0.25_wd1.0_scale1.0_s0 | 250 | None | 0.00% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.35_wd1.0_scale1.0_s0 | 250 | None | 8.48% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.36_wd1.0_scale1.0_s0 | 250 | None | 28.90% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.37_wd1.0_scale1.0_s0 | 250 | 35500 | 75.08% | LOCAL / NOT DURABLE |
| mlp_p31_h300_frac0.38_wd1.0_scale1.0_s0 | 250 | 23500 | 86.74% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.42_wd1.0_scale1.0_s0 | 250 | 17500 | 97.85% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.45_wd1.0_scale1.0_s0 | 250 | 13500 | 99.43% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.4_wd1.0_scale1.0_s0 | 250 | 20250 | 96.88% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.03_scale1.0_s0 | 100 | None | 0.00% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.08_scale1.0_s0 | 100 | None | 0.23% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.12_scale1.0_s0 | 100 | None | 0.46% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.18_scale1.0_s0 | 100 | None | 3.00% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.27_scale1.0_s0 | 100 | None | 9.47% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.4_scale1.0_s0 | 100 | 10800 | 59.58% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd0.6_scale1.0_s0 | 100 | 7300 | 100.00% | NO / NOT DURABLE |
| mlp_p31_h300_frac0.55_wd1.0_scale1.0_s0 | 100 | 4400 | 100.00% | NO / NOT DURABLE |

## Random lesions (30 of 300 units)

**mlp_p31_h300_frac0.55_wd0.4_scale1.0_s0/checkpoint_011000**: baseline 59.58% test; 5 random masks, ablation mean immediate loss 15.24pp (range 7.62-23.56); recovered by 150 updates in 2/5; steps [censored,censored,30,censored,20]; reset recovered in 1/5.

**mlp_p31_h300_frac0.55_wd1.0_scale1.0_s0/checkpoint_004400**: baseline 60.51% test; 5 random masks, ablation mean immediate loss 13.03pp (range 3.00-20.09); recovered by 150 updates in 5/5; steps [40,90,40,20,0]; reset recovered in 1/5.

**mlp_p31_h300_frac0.55_wd1.0_scale1.0_s0/checkpoint_004500**: baseline 64.20% test; 5 random masks, ablation mean immediate loss 13.53pp (range 3.70-21.02); recovered by 150 updates in 5/5; steps [40,90,30,40,10]; reset recovered in 1/5.

## Scientific limitations

The 5 masks are perturbations of the same learned network (NOT independent network replications). Both ablated checkpoints are on a rising generalization curve rather than a stable semi-grokking or smooth plateau. Weight decay and optimization duration differ. Baseline continuation improves without a lesion; recovery to 95% of *starting* baseline does not equal catch-up with continuing control.

The effect of the learning trajectory cannot be estimated from these comparisons. Further training and blinded reserved seeds are needed after finding the correct matched regimes.