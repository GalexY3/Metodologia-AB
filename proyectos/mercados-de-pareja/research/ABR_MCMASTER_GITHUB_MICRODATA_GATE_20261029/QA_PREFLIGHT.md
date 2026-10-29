# Pre-outcome freeze: McMaster original GitHub CSV, aggregate QA; NOT N83

Date 2026-10-29. Private project branch research/ab-r-mercados-pareja-20261028. This is a **noncycle descriptive data-quality audit**, not confirmatory ESBM experimentation. STOP_R5 maintained; only two McMaster sessions, no new external holdout, and no novel preregistered ESBM contrast.

**Source**: https://github.com/curlsloth/SpeedDating-BodySway at immutable public commit dadc819fbe99e99402b6d43f7e4f247a4bf55c2b.
File `SpeedDatingOSF_20201218.csv`; original Git blob SHA1 `9676ffc2022009c4ad878448a8d34b241d5396e8` recomputed independently and matched; SHA256 `9685dfb09a610bbf150ee2d151b05d6dceff6af18fc5b21d3ac31eecabf63eb6` computed before any y-values; 116,233 bytes, ASCII CRLF 719 rows, 17 columns, 54 actors and 2 sessions.
Pre-outcome structure: 719 unique directed keys, 714 reciprocal rows = 357 reconstructible encounters, 5 unmatched directed rows, no directed duplicate keys.
**Rights**: Authors' README grants CC BY-SA 4.0; LICENSE file contains CC BY 4.0 terms (conflict). No data redistribution, attribution to Chang et al. 2021; open creative-commons grant used with no account or signed agreement, no author contacted, no data published. The stricter CC BY-SA attribution terms are treated as caution until clarified.
**Frozen QA code**: `QA_CODE.js`, SHA256 50fb8df6b4e220182fafbeee4fb74ccc1390ecd1f97638e068c612b9487cdd8c. This specification and code MUST be committed before inspecting any outcome values, and read-after-write verified.

## Precommitted A-J structure (noncycle; no cycle authorization consumed)
A. Unit: (person i, person j, day) actual directed date record; only same-day inverse is counterpart.
B. Eligibility: one direction per (day,sub,partner); pair only if reciprocal record exists; count unmatched, duplicates, missing separately.
C. Outcome: original binary `meetAgain`; accept 1/0, no Likert thresholds, no imputation or inferred partner yes.
D. Scope: 2x2 native bilateral choice by sex, mutually yes/no and discordant; separate invalid codes. No inferential hypothesis tests or p-values.
E. Pure aggregate file QA: record count, unique actors, 2 session aggregates, missing, directed duplicates, reverse join counts, male and female decisions; no private row level output.
F. Descriptive metrics: male and female yes marginal shares among complete native binary encounters, both yes share, and naive product of marginals as a NONCAUSAL arithmetic comparator, no claim of matched independence under actor/event dependence.
G. Invariants: 2x2 valid+invalid equals reciprocal meeting count; 2*paired+unmatched equals directed rows only if no duplicate; publish only aggregate results.
H. No train/holdout in this audit; a split of these 2 sessions is NOT an independently collected external replicate. Zero evaluated models, no ESBM 2/3 success.
I. Strong scientific predecessors: Chang original movement/music regression, Joel/Baxter SRM, Pronk sequence rejection, Ogushi paired decisions, Matz language, Zhao permutations, independent site transport. All reserved for future true preregistered N83.
J. STOP_R5 remains because there is no independent external heldout real binary dataset and novel estimand/coded ESBM comparison. 0 valid/invalid/planning cycles from this QA. Never claim causal or transport validation.
