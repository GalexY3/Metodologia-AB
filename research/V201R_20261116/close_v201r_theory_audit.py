"""Freeze the executed diagnostic evidence without changing the user's Git state."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import subprocess
import importlib.metadata

B = Path(__file__).resolve().parent
REPO = B.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ledger_path = B/'results/V201R_AB_AUDIT_LEDGER.json'
    assert not ledger_path.exists()
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=REPO).decode('utf-8').strip())
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode('ascii').strip()
    index_sha = sha(gitdir/'index')
    score_sha = sha(B/'results/AB_PROGRESO_CT2_CT3.json')
    assert head == 'c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert index_sha == '0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert score_sha == '0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    reproduction = json.loads((B/'results/V201R_FRESH_REPRODUCTION.json').read_text(encoding='utf-8'))
    assert reproduction['reproduction'] == 'PASS'
    assert all(r['all_JSON_values_identical'] for r in reproduction['comparisons'])
    prior = [
      dict(authors='Brown; Taddei',year=2007,doi='10.1371/journal.pone.0000593',
           url='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0000593',
           read_scope='Abstract, conceptual model and Methods in primary HTML',
           relevance='Explicit durable public-good stock and ecological memory are established prior art.'),
      dict(authors='Baker; Gibbons; Murphy',year=2002,doi='10.1162/003355302753399445',
           url='https://faculty.washington.edu/mfan/is582/articles/Baker2002.pdf',
           read_scope='Abstract, introduction and main proposition; not all appendices',
           relevance='Asset ownership changes reneging incentives in relational contracts.'),
      dict(authors='Halac',year=2015,doi='10.1111/1756-2171.12080',
           url='https://business.columbia.edu/sites/default/files-efs/pubfiles/5700/Halac_HU.pdf',
           read_scope='Author original abstract and introduction, primary publication metadata; not a full proof audit',
           relevance='Relationship-specific upfront investment can improve relational incentives; observability matters. Close adversarial prior.'),
      dict(authors='Battaglini; Nunnari; Palfrey',year=2016,doi='10.1257/mic.20150126',
           url='https://snunnari.github.io/bnp_dyngvc_aej.pdf',
           read_scope='First five PDF pages, original publication page and replication-package metadata',
           replication_package='https://doi.org/10.3886/E114341V1',
           package_downloaded_or_analyzed=False,
           relevance='Human durable-public-good investment, reversibility, dynamic free riding and history dependence.'),
      dict(authors='Halonen-Akatwijuka; Pafilis',year=2020,doi='10.1016/j.jebo.2020.10.002',
           url='https://kclpure.kcl.ac.uk/ws/portalfiles/portal/136282775/Common_ownership_29_September_2020_JEBO_7Oct.pdf',
           read_scope='Abstract, introduction and model description through PDF page 9 using web extraction; not all propositions',
           local_download_status='403 from Bristol and KCL; web primary PDF readable; no local PDF fabricated',
           relevance='Repeated maintenance, common/joint ownership and incentive-compatible fines. Close public-good relational prior.'),
      dict(authors='Harstad; Lancia; Russo',year=2019,doi='10.1093/jeea/jvy055',
           url='https://www.tse-fr.eu/sites/default/files/econ/personer/vit/bardh/dokumenter/compliance.pdf',
           read_scope='Original abstract and introduction; not a complete theorem audit',
           relevance='Repeated technology investment and self-enforcing agreements; strategic investment affects compliance.'),
      dict(authors='Smith; Wen',year=2017,doi='10.1007/s40881-017-0033-2',
           url='https://link.springer.com/article/10.1007/s40881-017-0033-2',
           read_scope='Editorial abstract and metadata only; full text paywalled',
           relevance='Voting on public-good productivity investment, followed by voluntary contributions.'),
      dict(authors='Yamamoto; Goto',year=2024,doi='10.1038/s41598-024-73353-4',
           url='https://www.nature.com/articles/s41598-024-73353-4',
           read_scope='Article main text including Results, Discussion and Methods; PDF page 6 Table 4 rendered and inspected',
           original_dataset_previously_analyzed_as='V143/V144, not new external confirmation',
           relevance='Alternating/simultaneous PD with/without nonparticipation; no local capital mechanism.')
    ]
    prior_record = dict(review='Directed adversarial review, not exhaustive novelty proof',
        inspected_at_utc=datetime.now(timezone.utc).isoformat(),
        primary_sources=prior, no_third_party_PDF_redistribution=True,
        claim_capital_anchors_cooperation_not_sufficient_for_novelty=True)
    (B/'literatura/V201R_PRIOR_REVIEW.json').write_text(json.dumps(prior_record,indent=2),encoding='utf-8')
    files = ['v201r_theory_precheck.py','v201r_single_agent_bellman.py',
      'v201r_capital_coalition_audit.py','v201r_relational_certificate.py',
      'audit_v201r_capital_bounds.py','analyze_v201r_controls.py','reproduce_v201r.py',
      'research_resource_limits.py','REPRODUCE_V201R.md',
      'results/V201R_THEORY_PRECHECK.json','results/V201R_SINGLE_AGENT_BELLMAN.json',
      'results/V201R_CAPITAL_COALITION_AUDIT.json','results/V201R_RELATIONAL_CERTIFICATES.json',
      'results/V201R_CAPITAL_BOUND_INDEPENDENT_AUDIT.json','results/V201R_SCIENTIFIC_SYNTHESIS.json',
      'results/V201R_FRESH_REPRODUCTION.json','results/FIG_V201R_BOOTSTRAP_AND_DEVIATION.png',
      'results/INFORME_V201R_AUDITORIA_Y_CONTROLES_20261116.md',
      'handoff_codex/ESTADO_20261116_HYDROGEN_V201R.md',
      'docs/TFM_NOTA_V201R_VIABILIDAD_ANTES_DEL_APRENDIZAJE.md',
      'literatura/V201R_PRIOR_REVIEW.json',
      'theory_inputs/HYDROGEN_V201R_20261116/HYDROGEN_V201R_RECONSTRUCTION.txt']
    retained = ['results/V201R_THEORY_PRECHECK_ATTEMPT1_INPUT_MISSING.log',
      'results/V201R_PRECHECK_DRAFT1.py','results/V201R_THEORY_PRECHECK_DRAFT1.json',
      'results/V201R_THEORY_PRECHECK_FIRST_OUTPUT.json','results/V201R_SINGLE_AGENT_BELLMAN_FIRST_OUTPUT.json']
    ledger = dict(audit_id='V201R_HYDROGEN_20261116',
      status='POST_HOC_THEORY_AUDIT', timestamp_utc=datetime.now(timezone.utc).isoformat(),
      authorization='Persistent autonomous research explicitly authorized by the investigator; no new quota inferred from local templates.',
      parent_evidence=['V201 failed original proposal','V199 known private learners','V200 existing voluntary participation'],
      branch=dict(D_score=2.0,mechanism='Material stock investment and credibility of voluntary transfers',
                  CT2_historical_parent=61,CT2_new_branch=None),
      A='Check whether the supplied mechanism is viable before attributing outcomes to MARL.',
      B=['Private profitable bootstrap and self-enforcement as claimed','Investment coordination barrier and profitable payment deviations','Other contingent equilibria remain possible'],
      C='Deterministic counterexamples and constructive bounded controls; no statistical confirmatory claims.',
      D='Conditional outcome enumeration, exact rational inequalities, two different Bellman bounds, resource checks.',
      E=dict(controls_executed=5,analysis_steps=1,MARL_campaigns_executed=0,world_seeds=0),
      F='Counterexamples to the input and independent arithmetic/algorithm controls; same author, not an independent scientific team.',
      G=dict(fresh_staging_reproduction='PASS',same_machine=True,external_confirmation=False),
      H='Separate acquisition of capital, productive participation and enforcement. Original gamma band not established.',
      I=dict(internal_math='Supported within explicit control assumptions',emergence='Not tested',
             sociological_external_validity='Not established',novelty='Strong close antecedents; no novelty awarded'),
      J=dict(original_long_campaign='STOP_LOCAL_AS_WRITTEN',argument='REPAIR',overall_research_goal='CONTINUE_ACTIVE'),
      prior_art_review='literatura/V201R_PRIOR_REVIEW.json',
      new_N1_awards=[], N2=0,N3=0, canonical_score_changed=False,
      frozen_files={p:dict(sha256=sha(B/p),bytes=(B/p).stat().st_size) for p in files},
      retained_drafts_and_attempts={p:dict(sha256=sha(B/p),bytes=(B/p).stat().st_size) for p in retained},
      repair_history=['Input-path initial failure retained, not a scientific outcome',
        'Draft pivotality label corrected: necessary condition does not establish sequential equilibrium',
        'Bellman draft augmented with conservative first-action bounds; first output retained',
        'No preregistration claimed retroactively'],
      runtime=dict(python=platform.python_version(),packages={p:importlib.metadata.version(p) for p in ['numpy','numba','matplotlib']},
                   GPU_used=False,resource_limits='BelowNormal, six logical CPU affinity, Numba threads=2'),
      preservation=dict(local_HEAD=head,user_index_sha256=index_sha,canonical_score_sha256=score_sha))
    ledger_path.write_text(json.dumps(ledger,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='FROZEN',files=len(files),drafts=len(retained),preservation=ledger['preservation']),indent=2))


if __name__ == '__main__':
    main()
