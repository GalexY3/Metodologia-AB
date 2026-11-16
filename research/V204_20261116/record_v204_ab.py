"""Add evidence without changing the historical or canonical AB score."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent
ledger=dict(study='V204',status='REGISTERED_H1_FAIL',
    registration_commit='f8e9a55263584cfbd6248917b7c533d71af0a14a',
    A='Test whether established opponent-learning awareness changes acquisition with full net monetary costs',
    B=['LOLA-Ex acquires','One-step shaping insufficient in the specified cold neighborhood','Local shaping correction is too attenuated at a uniform start'],
    C='Ten specified deterministic points paired with existing EPG, two precision controls, stable-functionality criterion',
    D='2880 scalar derivative checks and 36 Hessian bilinear checks',
    E='Ten main and two precision flows completed; no eta or tolerance sweep',
    F='Independent JS literal evaluation: 42 profiles and 48 public best responses',
    G='Internal numerical confirmation; no external researcher or human-data confirmation',
    H='Post hoc exact payment-field identity with 57 component checks; novelty and broader numerical validation pending',
    I='Negative registered learning result; algebraic candidate scoped to uniform tabular count-history policies',
    J='STOP_LOCAL H1 claim; no eta sweep; falsify general-n and information-threshold identity and review priority',
    drift=dict(distance='D1',reason='Same game and objective; known opponent-aware gradient rule replaces own-only rule'),
    new_N1_awards=[],N2=0,N3=0,CT2_historical=61,new_branch_score=None,overall_goal='ACTIVE',
    current_goal_turn_classification='PROGRESS: registered V203/V204 runs, independent numerical checks and closed-form derivation',
    processes=dict(V204_session_32903='terminal_exit_0',technical_QA='terminal_exit_0',
                   JS_audit='terminal_exit_0',closed_form_certificate='terminal_exit_0'))
(B/'results/V204_AB_LEDGER.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
candidate=dict(id='CANDIDATE_LOLA_UNIFORM_COUNT_PAYMENT_IDENTITY',status='UNSCORED_CANDIDATE_NOT_N1_AWARD',
    parents=['V203_ORACLE_GRADIENT_CONTROL','FOERSTER_LOLA_2018_EQ4_4'],
    evidence=['V204_CLOSED_FORM_PAYMENT_GRADIENT.md','results/V204_CLOSED_FORM_CERTIFICATE.json'],
    priority_established=False,external_confirmation=False,
    discriminating_prediction_candidate='Sign of the directional local LOLA payment correction changes at a recipient-information threshold depending on donor risk; own-only payment gradient remains a cost',
    missing=['Independent variable-n / variable-signal implementation','Prior-art review of the precise identity','Evidence about learned outcomes or outside the model'],
    falsifier='Failure of the stated closed form or sign predictions under its assumptions in an independent implementation',
    nonclaims=['General cooperation transition','Every individual coordinate has the aggregate sign','General impossibility','Novel algorithm'])
(B/'results/V204_CANDIDATE_LEDGER.json').write_text(json.dumps(candidate,indent=2),encoding='utf-8')
fig,axs=plt.subplots(1,2,figsize=(10,3.4),layout='constrained')
for ax,lim in zip(axs,[(0,100),(55,65)]):
    ax.set_ylim(*lim);ax.set_xlim(-.45,3.45);ax.plot([0],[61],'o',color='#374a62')
    ax.annotate('61 histórico',xy=(0,61),xytext=(.1,lim[0]+.8*(lim[1]-lim[0])),fontsize=9)
    ax.axvspan(.6,3.4,color='#ddd',alpha=.5)
    ax.text(2,lim[0]+.4*(lim[1]-lim[0]),'Controles y candidato\nsin puntuación nueva',ha='center',fontsize=9)
    ax.set_xticks([0,1,2,3],['Previo','V202','V203','V204']);ax.set_ylabel('CT2');ax.grid(axis='y',alpha=.2)
axs[0].set_title('Escala completa');axs[1].set_title('Vista ampliada del registro histórico')
fig.suptitle('V204: ningún incremento por acumular controles o una fórmula posterior',fontsize=11)
fig.savefig(B/'results/FIG_V204_CT2_UNCHANGED.png',dpi=160);plt.close(fig)
print('V204 branch ledger and unscored candidate retained')
