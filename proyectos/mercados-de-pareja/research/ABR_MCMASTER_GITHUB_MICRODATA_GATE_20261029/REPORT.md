# Mercados de pareja AB-R -- McMaster author GitHub: original bilateral data and pre-outcome quality audit

**2026-10-29. Activity:** first actual access to the original anonymized 2020 McMaster speed-dating ANALYSIS CSV from the research author's [public GitHub](https://github.com/curlsloth/SpeedDating-BodySway). This is **same human cohort as SRC094**, not independent replication. **Noncycle quality audit, NOT AB-R N83**, and no causal or novel ESBM prediction evaluated.

## Source permissions, bytes and source code integrity
Original source commit dadc819fbe99e99402b6d43f7e4f247a4bf55c2b; [original CSV](https://github.com/curlsloth/SpeedDating-BodySway/blob/dadc819fbe99e99402b6d43f7e4f247a4bf55c2b/SpeedDatingOSF_20201218.csv); [original R script](https://github.com/curlsloth/SpeedDating-BodySway/blob/dadc819fbe99e99402b6d43f7e4f247a4bf55c2b/speedDatingOSF_20201218_win.r); [original scientific article](https://doi.org/10.1093/scan/nsaa093).
The author declares this GitHub copy duplicates OSF, but the present access was **exclusively via GitHub**. CSV has exactly **116233 bytes (ASCII/CRLF), 719 data rows, 17 columns**. Recomputed Git blob SHA1 matches GitHub: 9676ffc2022009c4ad878448a8d34b241d5396e8. Recomputed original CSV SHA256: **9685dfb09a610bbf150ee2d151b05d6dceff6af18fc5b21d3ac31eecabf63eb6**. This is a hash of the original record bytes, not an unrelated Git tree hash.
README declares **CC BY-SA 4.0** while LICENSE file text is **CC BY 4.0**. Both are open for attributed scientific analysis but the discrepancy remains unresolved; use conservative attribution/share-alike constraints and never rehost the source CSV or disaggregated individual rows. No personal identity or contact fields disclosed, no terms signed or authors contacted.

## Auditable PRE-OUTCOME freeze
Commit **5c96ba6e3b85722dcb497b58b1035ecbda283cd3** was pushed before examining any meetAgain response values. It contains [QA_PREFLIGHT.md](QA_PREFLIGHT.md), an A--J style noncycle protocol, and [QA_CODE.js](QA_CODE.js) exact source SHA256 **50fb8df6b4e220182fafbeee4fb74ccc1390ecd1f97638e068c612b9487cdd8c**. A separate, subsequent execution loaded the exact frozen code from the immutable Git commit, verified its SHA256, verified original data SHA256, then calculated ONLY the predeclared aggregate data-quality and 2x2 results. No original data or respondent-level output is stored here.
This is an audit contract, **NOT** a valid experimental N83 A--J preregistration or a model SHA freeze.

## Independent computed data-quality and descriptive results

**Structure and join:** 54 actors, two original sessions (358 and 361 directed records, each 27 actors), 719 unique (day,actor,partner) keys and zero duplicates. **714 directed rows have a corresponding reverse same-day record**, giving **357 actual complete two-person dates**. Five directed records have no reverse; their response is not treated as counterpart refusal. Invariants: 2 * 357 + 5 = 719; 70 + 86 + 151 + 50 = 357.

**Outcomes:** original binary column meetAgain contains 719 valid 0/1 records, 344 yes and 375 no, no other/missing. Among **357 complete real dates**:
| Native matched decisions | Encounters | Share |
|---|---:|---:|
| Both yes | **70** | **19.6%** |
| Both no | **86** | **24.1%** |
| Male yes, female no | **151** | **42.3%** |
| Female yes, male no | **50** | **14.0%** |
| **Total** | **357** | **100%** |

**201/357 = 56.3%** discordant. Among joined meetings male yes = (151+70)/357 = 221/357 = **61.9%** and female yes = (50+70)/357 = 120/357 = **33.6%**. Observed reciprocal 70/357 = **19.61%**; naive product of these marginals = **20.81%** (difference -1.20 percentage points); **NOT a calibrated independence test or causal finding** due repeated actors, venue/session eligibility and heterogeneity. There were zero invalid joint binary pairs and no inferential tests, models, simulations, p-values, splits or forecasts.

## R1-R5 and limitations

**R1:** only observed real dating opportunity followed by explicit, **self-reported** yes/no for *another date*; this is not observed contact exchange, stable relationship or relationship duration. Actor-choice is separate from pairwise mutual consent. No 5 unmatched reverse rows in dyadic rate denominators.
**R2:** original Chang models already use attractiveness, body sway and groove. Strong controls for any future novel ESBM prediction include SRM actor/partner/dyad of Joel and Baxter, sequence/rejection Pronk, behavioral predictors Ogushi, conversational Matz, Zhao permutation and event-order/popularity controls with matched information and budgets. None executed here.
**R3:** code/spec frozen before inspecting y, but solely for descriptive noncycle QA; no new model prereg or external holdout. Two McMaster sessions can only provide within-study splits; neither is a genuinely independent original sample. No causal or scientific 2/3 claim.
**R4:** novel future model would have to ablate assumed selection/sorting, exposure, attractive-partner ratings and timing, order/groove and missingness; account for clustering at 54 actors and two sessions. Observational associations do not identify causal direction.
**R5:** original legally open data route now confirmed and SHA256 computed; strict outstanding scientific gate is **independently collected external holdout, novel discriminating ESBM estimand, and competent frozen pre-outcome model**. **STOP_R5** still required: N83--N86 not opened.

## Ledger / interpretation
SRC096 registers a **new original file artifact** linked explicitly to **SRC094 same humans**. U126 materially improves P-DYADIC_ACCESS to VERIFIED_ORIGINAL_OPEN_NATIVE_BILATERAL_357_DYADS_TWO_SESSIONS_NO_EXTERNAL_HOLDOUT. U127 and U128 update existing priors with NO_CHANGE_WITH_REASON; this quality audit makes **zero new independent study and zero new 1/3, 2/3, 3/3 scientific discoveries**. Count **96 sources / 30 priors / 128 events**, **16/20 valid, four N83-N86 pending, CT2 ordinal 7/100**, no new point. [CT2 complete and zoom](../ABR_SSJY_STAGE_N82_20261029/CT2.svg) / [trajectory](../ABR_SSJY_STAGE_N82_20261029/CT2_TRAJECTORY.json).
No OSF web/API use, no Essex, Stanford, Gist, SSJY, no author contact, no license signed, no main merge or private data sharing. Clean clone was not independently run. All new code and this report are only on the research branch. Do not expend four already authorized slots for more descriptive analysis; a request for extra cycles is a separate prospective authorization and is not granted by this QA.
