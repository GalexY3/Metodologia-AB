"""An additive branch record; never edits the canonical score or user index."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent
ledger=dict(study='V203',status='COMPLETE_NEGATIVE_ACQUISITION',
    registration_commit='a73932856b9f88d27b166f3d0abc74be3dd154bb',
    A='Separate Monte Carlo incompetence from exact-gradient acquisition failure',
    B=['Exact own-gradient acquisition','Supplied-rule improvement without acquisition','History-blind natural-gradient invariant class'],
    C='Prospective 20 deterministic flows and four precision controls; no population inference',
    D='Two sets of 720 finite differences and 27/15-state equivalence',
    E='20 registered trajectories and four precision controls terminal, no optional stopping',
    F='Independent-language literal enumeration: 84 profiles, 96 public BR checks',
    G='Internal numerical confirmation only; external scientific replication absent',
    H='Local invariance lemma, original priority unestablished; LOLA and LIO already cover learning awareness',
    I='Negative in the specified cold neighborhood; supplied agreement can be improved',
    J='STOP_LOCAL acquisition claim in this oracle configuration; change causal mechanism, no rate sweep',
    drift=dict(distance='D1',reason='Same scientific question and physical game; estimator and optimization geometry replaced by oracle controls'),
    deterministic_sensitivity_points_not_worlds=True,new_N1_awards=[],N2=0,N3=0,
    CT2_historical=61,new_branch_score=None,overall_goal='ACTIVE',
    previous_goal_turn_classification='User-requested pause; no scientific execution during pause',
    current_goal_turn_classification='PROGRESS: new prospectively registered integrations, independent checks and retained negative')
p=B/'results/V203_AB_LEDGER.json';assert not p.exists();p.write_text(json.dumps(ledger,indent=2),encoding='utf-8')
prior=dict(study='V203',new_algorithm=False,originality_unestablished=True,records=[
    dict(work='Sutton et al., Policy Gradient Methods, 1999',role='Established policy-gradient theorem',new_priority_claim=False),
    dict(work='Kakade, A Natural Policy Gradient, 2001',role='Established Fisher geometry; derived discounted hierarchical control is not an author-code reproduction',new_priority_claim=False),
    dict(work='Foerster et al., LOLA, AAMAS 2018',role='Opponent-learning awareness already established',new_priority_claim=False),
    dict(work='Yang et al., LIO, NeurIPS 2020',role='Incentives through recipient learning; author code already has include_cost_in_chain_rule option',source_commit='979e29723aa9bf18fd63447bb58a2cc27ade6727',new_priority_claim=False),
    dict(work='Phan et al., MATE, 2024',role='Additional relevant rival; abstract/background read, full method audit pending',new_priority_claim=False),
    dict(work='McAvoy et al., Unilateral incentive alignment, PNAS 2025',role='Additional relevant rival; initial method reading only',new_priority_claim=False)])
(B/'results/V203_PRIOR_LEDGER.json').write_text(json.dumps(prior,indent=2),encoding='utf-8')
fig,axs=plt.subplots(1,2,figsize=(9.5,3.5),layout='constrained')
for ax,lim in zip(axs,[(0,100),(55,65)]):
    ax.set_ylim(*lim);ax.set_xlim(-.45,2.45)
    ax.plot([0],[61],'o',color='#374a62')
    ax.annotate('61: registro histórico',xy=(0,61),xytext=(.12,lim[0]+.76*(lim[1]-lim[0])),fontsize=9)
    ax.axvspan(.6,2.4,color='#dddddd',alpha=.45)
    ax.text(1.5,lim[0]+.38*(lim[1]-lim[0]),'V202 / V203\nsin puntuación asignada',ha='center',fontsize=9)
    ax.set_xticks([0,1,2],['Registro previo','V202','V203']);ax.set_ylabel('CT2');ax.grid(axis='y',alpha=.2)
axs[0].set_title('Escala completa');axs[1].set_title('Vista ampliada del registro histórico')
fig.suptitle('No se incrementa ni se traslada el 61 a una rama nueva',fontsize=12)
fig.savefig(B/'results/FIG_V203_CT2_UNCHANGED.png',dpi=160)
plt.close(fig)
print('V203 additive ledger and historical reference chart saved')
