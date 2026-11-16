# Joint advantage products can move an isolated Nash equilibrium

Research note, 16 November 2026. Internal mathematical and computational result; priority and external scientific confirmation remain open. No claim of a new cooperation algorithm or a learned institution.

## Claim under audit

Duque et al., *Advantage Alignment Algorithms*, ICLR 2025, define the advantage using the joint action in Section 2.3. Their Equation 8 adds a product of the agent's past advantages, the opponent's current advantage, and the agent's current policy score. Theorem 3 states that the alignment contribution vanishes at a Nash profile. Appendix A.8 invokes zero advantages at Nash. We distinguish the joint advantage from its conditional expectation over the other player's action: Nash indifference applies to the latter on the support of a best response. It does not make every joint-action advantage zero.

Primary source: [official ICLR paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/5185aa776fd64ae3b4c6dae1af1066b1-Paper-Conference.pdf), Sections 2.3 and 4, Equations 8 and 10, Theorem 3, Appendix A.8. The publisher PDF and arXiv v3 were both inspected. Their hashes are in the evidence package. No benchmark performance claim is tested here.

## A fully observed two-stage game

Both players choose independent binary actions in each stage. Write their signed first-stage actions as x,z in {−1,+1}, and their signed second-stage actions as f,g in {−1,+1}. The initial state is START; the next public state is z; after stage 1 the game absorbs. The time is therefore part of the state. With discount 0<γ<1 and c>0, rewards are

| Stage | Player 1 | Player 2 |
|---|---|---|
| 0 | z(1+cx) | −cxz |
| 1, public state z | cfg | f(z−cg) |

Each player has three independent Bernoulli logits, one per nonabsorbing state. Let π* put probability 1/2 on each action at every state. The c=0 version is a minimal example with dummy actions; the registered c=0.1 control removes those dummy actions. The primary conclusion uses both and does not depend on a flat equilibrium set.

**Proposition 1.** For c>0, π* is a Markov-perfect equilibrium. It is locally isolated among Markov-perfect profiles.

**Proof.** At either terminal state, player 1's action-value difference is 2c E[g]. Player 2's is −2c E[f]. Thus the unique terminal-stage mixed equilibrium has E[f]=E[g]=0 and both continuation values zero. The first-stage differences then are 2c E[z] and −2c E[x], forcing both initial probabilities to 1/2. This gives a backward-induction proof; at π* all unilateral policies give return zero. The independent symbolic check also evaluates the six indifference equations' Jacobian at π*: its determinant is 4096c^6. Hence the completely mixed solution is locally isolated. This is a mixed equilibrium, not a strict Nash equilibrium. □

At π*, all state values are zero and exact joint advantages equal the displayed stage rewards. Marginal own-action advantages vanish. A direct best-response check enumerates eight deterministic Markov policies per player; all have value zero against the other's uniform policy. History-dependent deviations cannot improve either: the other player's uniform terminal policy makes terminal own-action differences zero at every history, and the initial opponent action is uniform.

## The alignment field and a profitable deviation

Use detached exact advantages, normalized Bernoulli policies, and the expectation in Equation 8. Including the ordinary private-return policy gradient, the update direction is

\[
 F_i=\mathbb E\sum_t\gamma^t A^i_t S^i_t
 +\beta\mathbb E\sum_t\gamma^{t+1}
       \Big(\sum_{k<t}\gamma^{t-k}A^i_k\Big)A^j_t S^i_t,
 \qquad S^i_t=\nabla_{\theta_i}\log\pi_i(a^i_t|s_t).
\]

**Proposition 2.** At π*, for any c≥0,

\[
 F_1=(0,\beta\gamma^3/4,\beta\gamma^3/4),\qquad F_2=(0,0,0).
\]

**Proof.** The ordinary policy gradients vanish by indifference. There is no past term at t=0. For player 1 at t=1, write its terminal score as f/2 for the logit of the visited state. The advantage product times score is

\[
 z(1+cx)\, f(z-cg)\, f/2=(1+cx)(1-czg)/2.
\]

Conditional on z its expectation is 1/2; each terminal state has probability 1/2. Equation 8 contributes the factor βγ^3. For player 2 the corresponding product has zero expectation (the x and f factors have mean zero). All 16 trajectories are included, so this is a population expectation, not an estimate from a random minibatch. □

**Corollary.** After simultaneous ascent θ'=θ*+αF with α>0 and β>0, the profile is not Nash. Player 1's two terminal signed action means become m=tanh(αβγ^3/8)>0. Both on-policy expected returns are still zero. Player 2 can choose z=+1 initially and g=−1 at the reached terminal state, obtaining

\[
 \operatorname{BRgap}_2=\gamma(1+c)\tanh(\alpha\beta\gamma^3/8)>0.
\]

This is also the exact best-response gap because these choices maximize both positive terms and the initial reward still averages to zero over uniform x. Player 1's best-response gap remains zero. At γ=.9, β=.3, α=.1 and c=.1, each terminal field component is .054675 and player 2's gap is .0027064057579956335. Thus the operator both moves the profile and creates exploitability; it is not merely moving within a set of Nash equilibria.

## Why conditioning changes the conclusion

Let H_t contain the full history before current actions. Suppose current actions are conditionally independently sampled, advantages are detached, and W_i(H_t) is measurable before those actions. Define

\[
 \bar A_j(s_t,a^j_t)=\mathbb E_{a^i_t\sim\pi_i}[A_j(s_t,a^i_t,a^j_t)].
\]

The score identity yields

\[
 \mathbb E[W_i(H_t)\bar A_j(s_t,a^j_t)S^i_t\mid H_t,a^j_t]=0.
\]

Consequently, replacing only the **current opponent** advantage by this marginal in the exact-advantage Equation 8 removes its entire shaping field at every policy, while leaving the ordinary policy gradient unchanged. This is a different operator; it cannot be justified as lossless variance reduction of the joint-advantage product. The joint term can contain a nonzero conditional covariance with the current score even when its marginal advantage is zero.

The measurability condition matters. A past sampled GAE return may contain future rewards and need not be measurable with respect to H_t. The general cancellation statement above concerns exact past Q−V advantages or other genuinely pre-action weights. It is not a blanket cancellation theorem for every sampled-GAE implementation. At the equilibrium in this game, replacing the current opponent advantage by its exact marginal zero still cancels the term. Separately, the actual joint/sample-GAE helpers fail the equilibrium-preservation test for λ=0,.95,1 with exact state values. No imperfect critic is required.

Appendix A.8 also displays an additional inner expectation in Equation 66. Reading that inner expectation as an unconditional scalar changes the random coefficient in Equation 10. Our conclusion is about the joint-action operator in Equations 8/10 and the tested loss helpers, not every possible reading of that different displayed expression.

## Computational scope and reproducibility

The prospective registration was published and its bytes re-downloaded at commit c7779edf154a924262ddd60a579d7b9eafab0ba9 before the primary audit. The counterexample was analytically constructed before registration; this was not a blind search. The fixed deterministic design contains 320 literal profiles, not 320 independent stochastic replications. An additional 144 calls use unmodified AST-extracted bodies of the authors' GAE, alignment, and actor-loss functions, pinned to [commit 2065e43c0c36694965cf4476dc692512e3892dcc](https://github.com/jduquevan/advantage-alignment/tree/2065e43c0c36694965cf4476dc692512e3892dcc). Our fixture substitutes tabular log probabilities and exact critic values; it does not reproduce the authors' neural networks, environments, or training campaigns.

All 96 alignment configurations create a positive terminal field and a profitable deviation. All 48 naive policy-gradient controls stay fixed within their registered dtype tolerance. Source variants differ in temporal normalization and integrated versus separated losses; equality of their step-size scales is not claimed. A separately written JavaScript enumerator checks all fields and post-step best responses. An independent SymPy derivation checks the exact field, unilateral returns, Jacobian determinant, and regret formula. These implementations share project authorship and are not external scientific confirmation.

The post hoc marginalization intervention uses 12 off-equilibrium profiles and is explicitly separate from H1. It keeps exact past joint advantages and the private ordinary policy gradient. The joint shaping norm is at least .0239; replacing only the current opponent advantage leaves norm below 2.64×10^−18. This supports the causal interpretation within the specified operator.

## Interpretation and remaining uncertainty

The constructed counterexample contradicts universal Nash preservation for the specified joint-advantage operator. It does not show that shaping is irrational over a learning horizon, that cooperation is impossible, or that benchmark welfare improvements are false. Moving from Nash can even be desirable in a social dilemma; welfare and fixed-point preservation are distinct claims. This game establishes neither emergence of organization nor a human sociological law.

Priority remains unestablished. A bounded public search has not supplied a prior identical counterexample, but that absence is not evidence of novelty. OpenReview discussion access and source-search coverage are recorded explicitly. No authors have been contacted. The historical CT2 value 61 is unchanged; the mathematical candidate is unscored and has no new N1/N2/N3 award. A publishable correction would require independent scrutiny, a fuller priority review, and a narrowly accurate statement of which formulas and estimators it concerns.

Equilibrium instability in opponent shaping is established prior art: see Letcher et al., [Stable Opponent Shaping in Differentiable Games](https://arxiv.org/abs/1811.08469). The candidate here is the specific AA joint/marginal discrepancy and isolated-game certificate, not discovery of that general phenomenon. Only the abstract/introduction of SOS have been reviewed for this contextual comparison; its full method has not been reimplemented in this project.
