"""Freeze an explicit, licensed-source-conscious evidence package."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'research/V175_V180_20261115'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,obj):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    audit=json.loads((ROOT/'results/V175_V180_FINAL_AUDIT.json').read_text())
    build=json.loads((ROOT/'results/TFM_V180_BUILD.json').read_text())
    assert sha(ROOT/'docs/TFM_MANUSCRITO_TRABAJO_V180.md')==build['new_manuscript_sha256']
    for name,expected in build['source_hashes'].items():assert sha(ROOT/name)==expected
    freeze_specs=[('V175','results/v175_learned_memory/FREEZE.json','v175_memory_evolution.py','PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md'),
      ('V176','results/v176_frozen_memory/FREEZE.json','v176_frozen_memory_causal.py','PREREG_V176_FROZEN_MEMORY_CAUSAL.md'),
      ('V177','results/v177_gate_game/FREEZE.json','v177_cognitive_gate_game.py','PREREG_V177_COGNITIVE_GATE_GAME.md'),
      ('V178','results/v178_private_affine_M5/FREEZE.json','v178_private_affine_rival.py','PREREG_V178_PRIVATE_AFFINE_RIVAL.md'),
      ('V180','results/v180_open_policy_space/FREEZE.json','v180_open_policy_space.py','PREREG_V180_OPEN_POLICY_SPACE.md')]
    ledger=[]
    facts={
      'V175':('Evolve generic private memory without prescribed observer coefficients.',
              'High efficiency Q>=.70 and gain>=.15 in both seeds; full-information RNN diagnostic.',
              '10evolutions complete; high-capacity and diagnostic gates failed. Advantage only against the tested MLP.'),
      'V176':('Separate use of recurrence, sensory feedback, heterogeneity and invader exploitation.',
              'Frozen matched policies; RESET, sensory clamps, clones and one always-harvesting invader.',
              'Private recurrence helps; collective recurrence hurts Q; variable resource input dispensable in this evaluation.'),
      'V177':('Does all-memory equilibrium coexist with an ex-post Pareto benefit from disabling it?',
              'Enumerate all32gate profiles; strong-trap fraction>=.50 in both populations.',
              'Strong trap failed; aggregate improvement usually has individual losers. Restricted equilibria only.'),
      'V178':('Can a competent private affine rival close the efficiency gap?',
              '8seeds x5families; private affine high in6/8 and median gain>=.20; conditional M16.',
              'Primary failed0/8;M16cancelled. Private aspiration threshold Q=.5301; collective affine from scratch Q=.0356.'),
      'V180':('Does policy-space opening destroy maintenance and allow destructive affine invasion?',
              '8paired continuations; >=6/8losses. Four screening populations, four held-out validation populations.',
              'Maintenance-loss primary failed1/8;7/8retainQ>.30. Minimax bias b=0; destructive-invasion criterion failed.')}
    for study,freeze_name,source,protocol in freeze_specs:
        freeze=json.loads((ROOT/freeze_name).read_text())
        assert freeze['source_sha256']==sha(ROOT/source) and freeze['protocol_sha256']==sha(ROOT/protocol)
        a,c,g=facts[study]
        ledger.append(dict(study=study,kind='scientific_cycle_with_prospective_local_test',
          branching_distance='D2' if study=='V180' else 'D1',
          A_question=a,B_rivals='Itao/Kaneko; capacity and selection alternatives; Schmid2022; source-specific controls.',
          C_design=c,D_implementation_audit='See frozen pre-run audit and final464technicalchecks; not independent social confirmation.',
          E_execution='Completed; original outputs and all prespecified test populations preserved.',
          F_adversarial_checks='Strong rivals and falsifiers retained; no extra seeds or checkpoints chosen to rescue gates.',
          G_result=g,H_decision='STOP_LOCAL to rejected interpretation; do not extrapolate beyond tested families.',
          I_limits='Internal computational evidence; training seed is inference unit; no independent novel prediction confirmed.',
          J_preservation=dict(source=source,source_sha256=sha(ROOT/source),protocol=protocol,protocol_sha256=sha(ROOT/protocol),
                              remote_prereg=freeze['prereg_commit'],freeze_file=freeze_name),
          historical_CT2=61,new_branch_CT2=None,N2=0,N3=0))
    ledger.append(dict(study='V179',kind='existing_human_data_quality_and_reproduction_not_new_trial',branching_distance='D3_PLANNING_AB_ONLY_for_new_social_hypothesis',
       A_question='Can published monitoring data identify a new discriminating institutional prediction?',
       B_rivals='Government effect differs from zero versus government effect differs from public effect.',
       C_design='No new confirmatory hypothesis: scope to original main water-quality specification and a disclosed post-hoc direct contrast.',
       D_audit='ZIPhash/CRC,grain,keys,assignment consistency;160waterways,320rows;no household data.',
       E_execution='Python OLS,clusterCR2,Satterthwaite and10000author permutations reconstructed.',
       F_adversarial='Direct effect difference CI crosses0; source F critical-value bug checked and does not change this outcome specification.',
       G_result='Original evidence replicated; direct comparison not established.',
       H_decision='Do not use as confirmation of ecological or occupational mechanisms.',
       I_limits='Existing published sample; no new human observations; narrow outcome audit.',
       J_evidence='results/V179_HUMAN_POINT_AND_RANDOMIZATION_REPLICATION.json',historical_CT2=61,N2=0,N3=0))
    put(OUT/'LEDGER_A_J.json',dict(method='AB3.2.1',scientific_experiments=5,human_reproduction=1,
       tests_not_cycles=True,canonical_score_preserved=True,entries=ledger))
    environment=dict(python=platform.python_version(),platform=platform.platform(),
       packages={p:importlib.metadata.version(p) for p in ('numpy','numba','llvmlite','scipy','pandas','matplotlib')},
       max_workers=2,threads_per_worker=3,affinity_mask=16515072,priority='BelowNormal',CUDA_required=False)
    put(OUT/'ENVIRONMENT.json',environment)
    (OUT/'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in environment['packages'].items())+'\n',encoding='utf8')
    repo=ROOT.parents[2]
    def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True,encoding='utf8').strip()
    state=dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
       origin=git('remote','get-url','origin'),tracked_status=git('status','--porcelain=v1','--untracked-files=no'),
       publication_branch='research/aldea-memory-v175-20261115',prereg_head_before_results='2766f863cda02bff7cd67eebeb8a682de358065e')
    assert state['head']=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert 'GalexY3/Metodologia-AB' in state['origin']
    put(OUT/'GIT_STATE_BEFORE_PUBLICATION.json',state)
    readme=f'''# Evidence V175–V180 —15/11/2026

{audit['evolution_runs']}evolutions complete;{audit['passed']}technical checks;7retained failed/not-established scientific criteria. These counts are not discovery grades or independent human samples.

Read results/INFORME_V175_V180_20261115.md and REPRODUCE_V175_V180.md. The integrated TFM working draft has{build['words']}words and87bibliographic records with explicit review scope. It is not an approved final thesis. Historical CT2 remains61/100,N2=N3=0.

EVIDENCE.zip includes all new saved populations, curves, RNG/checkpoints, gate payoff tables, own source, protocols, figures, reports and selected prior context. It excludes the human ZIP, household data and third-party code without verified redistribution license. Retrieve originals from the links and hashes in their manifests. The prior V169–V174ZIP is a separate prerequisite only for the preservation-history checks, not the new training kernels.

SHA256.json lists every payload member. The ZIP contains the identical manifest under EVIDENCE_SHA256.json, which excludes itself to avoid a self-hash. PACKAGE_RECEIPT.json gives ZIPhash,CRCcheck and exact per-member verification. PUBLICATION_RECEIPT.json is written only after actual remote publication and is deliberately outside the frozen ZIP.

The user local branch,index and preexisting work are preserved. No PR or unsolicited messages are created. Goal remains active; this package closes a block, not the research objective.
'''
    (OUT/'README.md').write_text(readme,encoding='utf8')
    selected=set()
    def add(name):
        p=ROOT/name;assert p.is_file(),name;selected.add(p)
    own=['research_resource_limits.py','v175_memory_evolution.py','v176_frozen_memory_causal.py',
         'v177_cognitive_gate_game.py','v178_private_affine_rival.py','v179_download_cpr_evidence.py',
         'v179_profile_cpr_archive.py','v179_replicate_waterway_effects.py','v180_open_policy_space.py',
         'close_v175_v180.py','v180_register_and_integrate.py','archive_v175_v180.py','v180_verify_remote_prereg.py',
         'v180_verify_delivery.py','publish_v175_v180.ps1',
         'literatura/generate_bibliography.py','v169_local_private_contract_learning.py']
    for name in own:add(name)
    for _,_,_,protocol in freeze_specs:add(protocol)
    for directory in ('results/v175_learned_memory','results/v176_frozen_memory','results/v177_gate_game',
                      'results/v178_private_affine_M5','results/v180_open_policy_space'):
        for p in (ROOT/directory).rglob('*'):
            if p.is_file() and p.suffix in ('.json','.jsonl','.npz'):selected.add(p)
    for pattern in ('V175*.json','V176*.json','V178*.json','V179*.json','V180*.json',
                    'AB_EVALUACION_V175_V180*.json','TFM_V180_BUILD.json','FIG_V175*.png','FIG_V179*.png','FIG_CT2_V175*.png'):
        for p in (ROOT/'results').glob(pattern):selected.add(p)
    for p in (ROOT/'results').glob('V17*_CONSOLE.log'):selected.add(p)
    for name in ('results/V180_CONSOLE.log','results/V180_VALIDATION_CONSOLE.log',
                 'REPRODUCE_V175_V180.md','V175_REPRODUCTION.md',
                 'results/INFORME_V175_V180_20261115.md','handoff_codex/ESTADO_20261115_V180.md',
                 'docs/TFM_MANUSCRITO_TRABAJO_V180.md','docs/TFM_MANUSCRITO_TRABAJO_V174.md',
                 'literatura/references_verified.json','literatura/references.bib','literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md',
                 'literatura/original_code/V173_DOWNLOAD_MANIFEST.json',
                 'datos_humanos/metaketa_china_2021/DOWNLOAD_MANIFEST.json','datos_humanos/metaketa_china_2021/OSF_METADATA.json'):
        add(name)
    for p in (ROOT/'docs').glob('TFM_CAPITULO*.md'):selected.add(p)
    for name in build['source_hashes']:add(name)
    prior=json.loads((ROOT/'results/V166_CROSS_CYCLE_TECHNICAL_AUDIT.json').read_text())
    for r in prior['checks']:
        if r.get('check')=='results_file_exists':add('results/'+r['file'])
    for name in ('results/V166_CROSS_CYCLE_TECHNICAL_AUDIT.json','results/V167_CORRELATED_APPROVAL_K4_K12.json',
                 'results/V167A_EXACT_CERTIFICATION_AUDIT.json','results/V169_V174_FINAL_AUDIT.json'):
        add(name)
    for p in OUT.rglob('*'):
        if p.is_file() and p.name not in ('EVIDENCE.zip','SHA256.json','PACKAGE_RECEIPT.json','PUBLICATION_RECEIPT.json') and not p.name.startswith('git_publish'):
            selected.add(p)
    assert all(p.suffix not in ('.xlsx','.xls') for p in selected)
    assert not any(p.name.startswith('Itao_ds_game_') or p.name.startswith('Buntaine2021_UrbanWaterways_') for p in selected)
    payload=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(selected)]
    manifest=dict(scope='Own evidence and selected prior context; originals excluded as documented.',files=payload)
    manifest_text=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n';(OUT/'SHA256.json').write_bytes(manifest_text.encode('utf8'))
    archive=OUT/'EVIDENCE.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for r in payload:z.write(ROOT/r['path'],r['path'])
        z.writestr('EVIDENCE_SHA256.json',manifest_text)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={r['path'] for r in payload}|{'EVIDENCE_SHA256.json'}
        assert z.read('EVIDENCE_SHA256.json')==manifest_text.encode('utf8')
        for r in payload:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    receipt=dict(archive='research/V175_V180_20261115/EVIDENCE.zip',bytes=archive.stat().st_size,
       sha256=sha(archive),payload_files=len(payload),manifest_members=1,CRC_verified=True,
       every_member_SHA256_verified=True,source_payload_hashes_verified=True,
       human_raw_ZIP_excluded=True,third_party_unlicensed_code_excluded=True,
       CT2_historical=61,N2=0,N3=0,goal_active=True,packaging_revision=2,
       supersedes_archive_sha256='2b6e2b650b73d7fcee9816774a2d5d310dede9dd5c3b45d3792dad12d67b5587',
       revision_reason='Exact manifest bytes and Git blob roundtrip; scientific inputs and results unchanged.')
    put(OUT/'PACKAGE_RECEIPT.json',receipt)
    print('ARCHIVED',json.dumps(receipt),flush=True)


if __name__=='__main__':main()
