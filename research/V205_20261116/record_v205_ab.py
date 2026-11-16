"""Append a scoped, unscored mathematical candidate; no canonical score change."""
from pathlib import Path
import hashlib
import json

B=Path(__file__).resolve().parent
assert hashlib.sha256((B/'results/AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest()=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
ledger=dict(study='V205',status='REGISTERED_H1_CONFIRMED_INTERNAL',
    A='Does the joint-advantage AA operator preserve every Nash profile as claimed?',
    B=['Nash marginal indifference suffices','Joint advantage covariance generates a nonzero score product','Movement only follows degeneracy, imperfect critics or finite samples'],
    C='Prospective analytical game; c=0 minimal and c=.1 isolated-equilibrium control; exact Eq8/59 and original loss helper audit',
    D='Four off-primary technical policies, 48 scalar gradient checks; frozen source and remote byte verification',
    E='320 literal deterministic profiles and 144 original-source helper calls completed; 96 AA positive, 48 naive controls stationary within tolerance',
    F='Independent JS enumeration and symbolic exact certificates; equilibrium isolation; positive post-step BR gap',
    G='No external scientific confirmation; bounded priority search incomplete; OpenReview unavailable',
    H='Post hoc opponent-current marginalization intervention at 12 off-equilibrium profiles; cancellation proof has pre-action measurability restriction',
    I='Specific universal preservation claim contradicted for the stated joint operator; no welfare, institution-emergence or human-law claim',
    J='Preserve and publish full counterexample; seek independent scrutiny when authorized; broader cooperation goal remains active',
    drift=dict(parent_domain='Private-return cooperation and opponent-learning-aware gradients V203/V204',
        child_domain='Equilibrium-preservation audit of a published cooperation operator',D_score=2,
        what_changes=['Two-player two-stage population','Estimand changes from learned acquisition to local Nash preservation'],
        what_transfers=['Exact policy gradients','Best-response certificates','Distinction between rule and learned outcome'],
        prior_art_gate='Specific counterexample priority remains unestablished',
        rivals=['Original AA theorem3','Marginal-advantage interpretation','Known LOLA equilibrium instability, not itself novel'],
        novel_evidence_required=['Independent scrutiny of the counterexample','Fuller priority review'],
        CT2_before_after=dict(historical=61,candidate=None),
        selection_exposure='Counterexample constructed analytically before registration, not blind search'),
    registration_commit='c7779edf154a924262ddd60a579d7b9eafab0ba9',
    new_N1_awards=[],N2=0,N3=0,historical_CT2=61,new_branch_score=None,overall_goal='ACTIVE',
    current_goal_turn_classification='PROGRESS: registered published-method falsification, source helper tests, exact proof and causal intervention',
    process_status=dict(primary='terminal_exit_0',JS='terminal_exit_0',symbolic='terminal_exit_0',posthoc='terminal_exit_0'))
candidate=dict(id='CANDIDATE_AA_JOINT_MARGINAL_NASH_COUNTEREXAMPLE',status='UNSCORED_NOT_N1_AWARD',
    parents=['V204_OPPONENT_SHAPING_AUDIT','DUQUE_ETAL_ICLR2025'],
    evidence=['V205_NASH_COUNTEREXAMPLE_NOTE.md','results/V205_ADVALIGN_NASH_AUDIT',
              'results/V205_SYMBOLIC_CERTIFICATE.json','results/V205_NODE_INDEPENDENT_AUDIT.json'],
    priority_established=False,external_confirmation=False,
    prediction='Exact joint Eq8 moves an isolated mixed Nash profile with terminal field beta*gamma^3/4, creating BRgap2=gamma*(1+c)*tanh(alpha*beta*gamma^3/8)',
    falsifier='An error in the Nash certificate or population score-product field, or a relevant theorem hypothesis that excludes the specified game/operator',
    limitations=['Internal shared authorship','No full original benchmark reproduction','Priority review incomplete',
                 'No claim of institution acquisition','No human-data confirmation'],
    contribution_scope='Potential mathematical correction and causal conditioning diagnosis; not a new algorithm or general impossibility')
for name,data in [('V205_AB_LEDGER.json',ledger),('V205_CANDIDATE_LEDGER.json',candidate)]:
    out=B/'results'/name;assert not out.exists();out.write_text(json.dumps(data,indent=2),encoding='utf-8')
print('V205 unscored candidate and A-J ledger recorded; canonical CT2 unchanged')
