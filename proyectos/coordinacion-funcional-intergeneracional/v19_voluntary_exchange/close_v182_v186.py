"""Evidence-based closure. Refuses to close before all scientific jobs finish."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
RESULTS = BASE/'results'


def read(path):
    return json.loads((BASE/path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bibliography():
    files = ['references_verified.json', 'references.bib', 'BIBLIOGRAFIA_ACUMULATIVA_20261114.md']
    backup = BASE/'literatura/backups/V182_V186_20261115'
    backup.mkdir(parents=True, exist_ok=False)
    for name in files:
        shutil.copy2(BASE/'literatura'/name, backup/name)
    catalog = read('literatura/references_verified.json')
    refs = catalog['references']
    yaman = next(r for r in refs if r['id'] == 'Yaman2023')
    yaman.update(url='https://pmc.ncbi.nlm.nih.gov/articles/PMC10598450/',
                 verification='main text, 13-page supplement text, CC0 MATLAB source executed, all 1200 archived fits audited',
                 full_text_reviewed=True, checked_on='2026-11-15',
                 our_experiments='V182 original archive audit; V183 hazard timing; V184 frozen pasture replay',
                 novelty_constraint='Mandatory individual sanctions and group-level norm selection explicitly acknowledged by authors; archived pasture code/data mismatch does not refute paper automatically.')
    entries = [
        dict(id='YangEtAl2020LIO', authors='Yang, Jiachen; Li, Ang; Farajtabar, Mehrdad; Sunehag, Peter; Hughes, Edward; Zha, Hongyuan', year=2020,
             title='Learning to Incentivize Other Learning Agents', container='NeurIPS33:15208–15219',
             url='https://proceedings.neurips.cc/paper_files/paper/2020/hash/ad7ed5d47b9baceb12045a929e7e2f66-Abstract.html',
             contribution='Private learned incentives and division of labor; meta-gradients and opponent models.',
             novelty_constraint='Do not claim private incentive learning or its inter-episode credit problem as new.', verification='full main text through conclusion; appendix and original implementation not reproduced'),
        dict(id='PowerEtAl2022Grokking', authors='Power, Alethea; Burda, Yuri; Edwards, Harri; Babuschkin, Igor; Misra, Vedant', year=2022,
             title='Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets', container='arXiv2201.02177',
             url='https://arxiv.org/abs/2201.02177', contribution='Delayed generalization after fitting algorithmic data.',
             novelty_constraint='A late test-accuracy increase is an established phenomenon.', verification='primary abstract and bibliographic metadata'),
        dict(id='NandaEtAl2023ProgressGrokking', authors='Nanda, Neel; Chan, Lawrence; Lieberum, Tom; Smith, Jess; Steinhardt, Jacob', year=2023,
             title='Progress Measures for Grokking via Mechanistic Interpretability', container='ICLR2023',
             url='https://arxiv.org/abs/2301.05217', contribution='Mechanistic progress measures for modular-addition grokking.',
             novelty_constraint='Thresholded accuracy does not by itself identify sudden mechanism formation.', verification='primary paper bibliographic record and task scope; full text review pending'),
        dict(id='ChaabouniEtAl2020Generalization', authors='Chaabouni, Rahma; Kharitonov, Eugene; Bouchacourt, Diane; Dupoux, Emmanuel; Baroni, Marco', year=2020,
             title='Compositionality and Generalization In Emergent Languages', container='ACL2020:4427–4442', doi='10.18653/v1/2020.acl-main.407',
             url='https://aclanthology.org/2020.acl-main.407/', contribution='Generalization of learned communication and separability from compositionality.',
             novelty_constraint='Communication generalization and transmission to new agents are not new generic claims.', verification='primary abstract and metadata'),
        dict(id='LoweEtAl2019CommunicationPitfalls', authors='Lowe, Ryan; Foerster, Jakob; Boureau, Y-Lan; Pineau, Joelle; Dauphin, Yann', year=2019,
             title='On the Pitfalls of Measuring Emergent Communication', container='AAMAS2019:693–701',
             url='https://ifaamas.org/Proceedings/aamas2019/pdfs/p693.pdf', contribution='Information correlation alone does not establish causal communication.',
             novelty_constraint='Use causal and distribution-preserving message interventions.', verification='primary abstract and methodological excerpts'),
        dict(id='HutteggerEtAl2014SignalingDynamics', authors='Huttegger, Simon; Skyrms, Brian; Tarrès, Pierre; Wagner, Elliott', year=2014,
             title='Some dynamics of signaling games', container='PNAS111(Suppl3):10873–10880', doi='10.1073/pnas.1400838111',
             url='https://pmc.ncbi.nlm.nih.gov/articles/PMC4113927/', contribution='Evolution and learning of signaling conventions with aligned or conflicting interests.',
             novelty_constraint='Partial communication and pooling equilibria have strong classical antecedents.', verification='primary abstract, introduction and pooling-dynamics excerpts'),
        dict(id='SpikeEtAl2017LearnedSignaling', authors='Spike, Matthew; Stadler, Kevin; Kirby, Simon; Smith, Kenny', year=2017,
             title='Minimal Requirements for the Emergence of Learned Signaling', container='CognitiveScience41(3):623–658', doi='10.1111/cogs.12351',
             url='https://pmc.ncbi.nlm.nih.gov/articles/PMC5412673/', contribution='Comparative models of reinforcement, forgetting and bias against ambiguity.',
             novelty_constraint='A generic ambiguity/forgetting explanation cannot be claimed new; use these as competent rivals.', verification='primary abstract and relevant reinforcement/information-loss sections; full review pending'),
    ]
    known = {r['id'] for r in refs}
    fresh = [r for r in entries if r['id'] not in known]
    for r in fresh:
        r.update(theme='COMMUNICATION_AND_LEARNING', full_text_reviewed=False,
                 checked_on='2026-11-15', our_experiments='V185–V186 and prospective strong-rival audit')
        refs.append(r)
    catalog['number_verified'] = len(refs)
    catalog['review_date'] = '2026-11-15'
    (BASE/'literatura/references_verified.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
    bib = (BASE/'literatura/references.bib').read_text(encoding='utf-8')
    for r in fresh:
        bib += '\n@misc{'+r['id']+',\n'+',\n'.join('  '+key+' = {'+str(value)+'}' for key,value in
                   [('author',r['authors'].replace('; ', ' and ')),('title',r['title']),('year',r['year']),('url',r['url'])])+ '\n}\n'
    (BASE/'literatura/references.bib').write_text(bib, encoding='utf-8')
    md = (BASE/'literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md').read_text(encoding='utf-8')
    md = re.sub(r'\*\*87 fuentes verificadas bibliográficamente; 0 pendientes\*\*',
                f'**{len(refs)} fuentes verificadas bibliográficamente; 0 pendientes**', md, count=1)
    md += '\n\n## Actualización V182–V186: código original y comunicación\n\nYaman2023 pasa de resumen a lectura del texto principal y auditoría ejecutada. El código archivado y los datos no tienen la misma interfaz ni regularizador; no se invalida automáticamente el artículo. Las fichas nuevas conservan su alcance de lectura, que no equivale a revisión completa.\n\n'
    for r in fresh:
        md += f"**{r['authors']} ({r['year']}).** [{r['title']}]({r['url']}). {r['container']}.\n\n{r['contribution']} Restricción: {r['novelty_constraint']} Alcance: {r['verification']}.\n\n"
    (BASE/'literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md').write_text(md, encoding='utf-8')
    return fresh, len(refs)


def main():
    assert not (RESULTS/'INFORME_V182_V186_20261115.md').exists()
    original = read('results/V182_YAMAN_ARCHIVE_AUDIT/archive_audit.json')
    parity = read('results/V182_OCTAVE_VALIDATION/parity_audit.json')
    timing = read('results/V183_HAZARD_TIMING/SUMMARY.json')
    pasture = read('results/V184_PASTURE_REPLAY/SUMMARY.json')
    pilot = read('results/V185_COLLECTIVE_GROKKING/SUMMARY.json')
    causal = read('results/V186_INFORMATION_BOTTLENECK/SUMMARY.json')
    preaudit = read('results/V186_INFORMATION_BOTTLENECK/PREAUDIT.json')
    replay = read('results/V186_INFORMATION_BOTTLENECK/UPDATE_REPLAY_AUDIT.json')
    assert len(original['rows']) == 1200 and not parity['failures']
    assert all(r['passed'] for r in replay)
    assert timing['primary_gate_passed'] is False
    metric_rows = [read(str(p.relative_to(BASE))) for p in sorted((RESULTS/'V183_HAZARD_TIMING').glob('norm_*.json'))]
    metrics = np.array([r['metrics'] for r in metric_rows])
    audit = dict(original_fits=1200, maximum_original_fitness_L0_residual=max(abs(r['fitness_residual_l0']) for r in original['rows']),
                 original_code_cross_language_checks=len(parity['checks']), cross_language_failures=0,
                 original_wiring_and_regularizer=parity['original_wiring_and_regularizer'],
                 timing_technical_checks=len(read('results/V183_TECHNICAL_GATE.json')['checks']),
                 maximum_transfer_conservation_error=float(metrics[:,:,:,3].max()),
                 maximum_conditional_identity_error=float(metrics[:,:,:,4].max()),
                 maximum_zero_hazard_paired_path_error=float(metrics[:,:,:,7].max()),
                 timing_primary_failed_as_preregistered=True, pasture_unique_lives=1680,
                 total_new_Yaman_lifetime_evaluations=6480, pilot_training_runs=4,
                 canceled_conditional_V185_freezes=4, cancellation_reason='Neither independent pair reached train99%',
                 old_update_replay_exact=all(max(r['errors'].values()) == 0 and r['exact_rng'] for r in replay),
                 original_V185_restore_helper_latent_bug='CUDA map_location moves generator state; unused freezes were not run. V186 restores CPU ByteTensor, old trajectories replay exactly.',
                 source_archive_bytes=252169955, source_archive_SHA256='c152434d267e7992284077183456d853569bef74cb4ff7e95c7a86689f553b45',
                 new_collective_grokking_accredited=False, CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    assert max(audit[k] for k in ['maximum_transfer_conservation_error','maximum_conditional_identity_error','maximum_zero_hazard_paired_path_error']) <= 1e-10
    (RESULTS/'V182_V186_FINAL_AUDIT.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')

    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    fig, ax = plt.subplots(1,2,figsize=(11,4.2))
    effect, ci = timing['primary_effect'], timing['hierarchical_bootstrap_CI95']
    ax[0].errorbar(effect,0,xerr=np.array([[effect-ci[0]],[ci[1]-effect]]),fmt='o',capsize=5,color='#156f79')
    ax[0].axvline(.25,ls='--',color='#b54a35',label='Margen previo 0,25')
    ax[0].axvline(0,color='gray',lw=.8);ax[0].set(ylim=(-.6,.6),yticks=[],xlabel='Recompensa ORIGINAL − ATAQUE_PRIMERO',title='V183: hipótesis principal fallida')
    ax[0].legend(fontsize=9)
    ax[1].bar(['Código publicado','Asignación invertida'],[pasture['RMSE_release'],pasture['RMSE_swapped']],color=['#156f79','#b54a35'])
    ax[1].set(ylabel='RMSE frente al valor archivado',title='V184: reproducción aproximada')
    fig.suptitle('Auditoría de Yaman: 30 bloques originales; no formación institucional privada',fontsize=12)
    fig.tight_layout();fig.savefig(RESULTS/'FIG_V182_V184_REPRODUCTION.png',dpi=180);plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(12,4.5))
    for axis, seed in zip(axes,[185115,185116]):
        for condition,color in [('FIXED_PROTOCOL','#156f79'),('INDEPENDENT_COMM','#b54a35')]:
            r=read(f'results/V185_COLLECTIVE_GROKKING/{condition}_s{seed}/metrics.json')
            axis.plot([v['step']/1000 for v in r['history']],[v['test'] for v in r['history']],color=color,label=condition)
        bound=next(r for r in preaudit if r['seed']==seed)['original_bounds']['test']
        axis.axhline(bound,color='gray',ls=':',label='Techo test del código aprendido final')
        axis.set(xlabel='Actualizaciones (miles)',ylabel='Precisión en pares nuevos',ylim=(0,1.03),title=f'Historia {seed}')
    axes[0].legend(fontsize=8);fig.suptitle('V185: el control individual generaliza tarde; los dos agentes pierden información')
    fig.tight_layout();fig.savefig(RESULTS/'FIG_V185_DELAYED_GENERALIZATION.png',dpi=180);plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(12,4.5))
    for axis, seed in zip(axes,[185115,185116]):
        for mode,color in [('CONTINUE_JOINT','#b54a35'),('FROZEN_ORIGINAL','#8874a8'),('BIJECTIVE_REPAIR','#156f79')]:
            r=read(f'results/V186_INFORMATION_BOTTLENECK/{mode}_s{seed}/metrics.json')
            axis.plot([v['step']/1000 for v in r['history']],[v['test'] for v in r['history']],color=color,label=mode)
        axis.axhline(.95,color='gray',ls=':')
        axis.set(xlabel='Actualizaciones totales (miles)',ylabel='Precisión en pares nuevos',ylim=(0,1.03),title=f'Historia {seed}')
    axes[0].legend(fontsize=8);fig.suptitle('V186: mismo presupuesto; reparación externa del código, no institución aprendida')
    fig.tight_layout();fig.savefig(RESULTS/'FIG_V186_CAUSAL_BOTTLENECK.png',dpi=180);plt.close(fig)

    ptable='\n'.join(f"| {r['seed']} | {r['condition']} | {100*r['final']['train']:.2f}% | {100*r['final']['test']:.2f}% | {r['t_mem']} | {r['t_gen']} |" for r in pilot['runs'])
    ctable='\n'.join(f"| {g['seed']} | {100*g['scores']['CONTINUE_JOINT']:.2f}% | {100*g['scores']['FROZEN_ORIGINAL']:.2f}% | {100*g['scores']['BIJECTIVE_REPAIR']:.2f}% | {g['gate_passed']} |" for g in causal['gates'])
    report=(BASE/'docs/V182_V186_REPORT_TEMPLATE.md').read_text(encoding='utf-8').format(audit=audit, effect=effect, ci=ci, pasture=pasture, ptable=ptable, ctable=ctable, causal=causal)
    (RESULTS/'INFORME_V182_V186_20261115.md').write_text(report, encoding='utf-8')
    fresh, nrefs = bibliography()
    chapter = report.replace('# V182–V186: reproducción adversarial y límites del grokking entre agentes',
                             '## Código publicado, riesgo material y generalización entre agentes',1)
    chapter = chapter.replace('\n## ', '\n### ').replace('(FIG_', '(../results/FIG_')
    (BASE/'docs/TFM_CAPITULO_REPRODUCCION_Y_GROKKING.md').write_text(chapter, encoding='utf-8')
    parent = BASE/'docs/TFM_MANUSCRITO_TRABAJO_V181.md'
    manuscript = parent.read_text(encoding='utf-8')
    manuscript = manuscript.replace('ampliado hasta V181','ampliado hasta V186',1)
    manuscript = manuscript.replace('las campañas V169–V181','las campañas V169–V186',1)
    manuscript = manuscript.replace('[Yaman et al., preprint de 2022](https://arxiv.org/html/2208.05568v3)',
                                    '[Yaman et al. (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10598450/)')
    marker='\n## Discusión integrada'
    assert manuscript.count(marker)==1
    manuscript=manuscript.replace(marker,'\n'+chapter+'\n'+marker,1)
    manuscript += '\n\n### Referencias añadidas para V182–V186\n\n'+'\n\n'.join(
        f"{r['authors']} ({r['year']}). *{r['title']}*. {r['container']}. [Fuente primaria]({r['url']})." for r in fresh)+'\n'
    output=BASE/'docs/TFM_MANUSCRITO_TRABAJO_V186.md'
    assert not output.exists()
    output.write_text(manuscript,encoding='utf-8')
    evaluation=dict(method='AB3.2.1',date='2026-11-15',canonical_CT2_historical=61,new_branch_score=None,
                    N1='NOT_AUDITED',new_original_N1_awarded=False,N2=0,N3=0,
                    primary_timing_failed=True,approximate_reproduction_not_originality=True,
                    collective_grokking_not_accredited=True,oracle_repair_not_learned_institution=True,
                    V186_primary=causal['primary_passed'],goal_status='active',
                    manuscript_sha256=sha(output),manuscript_words=len(manuscript.split()),bibliographic_records=nrefs)
    (RESULTS/'AB_EVALUACION_V182_V186_20261115.json').write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
    ledger=[]
    for study,kind,outcome in [('V182','POSTHOC_REPRO_AUDIT','code/data mismatch;51 cross-language checks'),
                               ('V183','PREREG_CAUSAL_TEST','primary failed'),('V184','PREREG_DESCRIPTIVE_REPLAY','mapping correspondence;approximate reproduction'),
                               ('V185','PREREG_DISCOVERY_PILOT','individual positive control;no memorization in independent pairs'),
                               ('V186','PREREG_CAUSAL_FOLLOWUP',str(causal['primary_passed']))]:
        ledger.append(dict(id=study,kind=kind,outcome=outcome,A='uncertainty in report',B='explicit rival',C='prior claims restricted',
                           D='source and protocol frozen where prospective',E='executed artifacts',F='full outcomes retained',
                           G='declared criterion assessed',H='technical validation distinguished from scientific confirmation',
                           I='novelty not established',J='no CT2 increase;global goal active',new_N1=False,N2=False))
    (RESULTS/'V182_V186_AB_LEDGER.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
    handoff=f'''# Estado V186 — 15/11/2026

Objetivo ACTIVO,incluido grokking colectivo solicitado por el usuario. No se concede2/3ni se cambiaCT2histórico61. Nueva rama sin puntuación. Leer results/INFORME_V182_V186_20261115.md y docs/TFM_MANUSCRITO_TRABAJO_V186.md. Manuscrito:{evaluation['manuscript_words']}palabras,{nrefs}fichas bibliográficas con alcance de lectura explícito;no esTFMfinalaprobado.

Todos los jobsV182–V186terminaron. V183margen.25falla conefecto.0548931. V184reproducciónaproximada,RMSErelease.8426vsswap4.0267. V185diccionariofijogrokkingindividual2/2,paresprivadossinmemorizar2/2;congelacionescondicionalescanceladas. V186gate:{causal['primary_passed']};resultados completos en SUMMARY.json. Reparación esoráculoexógeno. No afirmar nuevoequilibriopooling,olvidooincentivosprivados:antecedentesLIO,signalinggamesySpike2017yaexisten.

Siguienteincertidumbre:rivalprivadocompetentedeconvenciones(Roth–Erev/antiambigüedadsegúnfuenteoriginal),ypruebadequeunatransicióndependedemásdeunaprendiz. No multiplicarREINFORCEsinresolveresecuello. Datoshumanosanterioresnocorroboranestatareasintética. NoCONTACTARautores.

GitlocalHEADc032a32d2d8d7710a6ad5a88519b0801ea186891eíndiceconhash0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1preservados. Remotopropioactualantesdecierre4164292c0d32adcb58c2d9ce4e944427578b8da2,rama research/aldea-memory-v175-20261115. Consultarrecibodepublicaciónparacommitfinal;noasumirqueestepreregcontieneresultados.

OctaveportátilC:/Programación/tools/octave-11.3.0;originalYaman252MBenliteratura/original_code/Yaman2023,licenciaCC0. Conservaroriginal. ParserinicialinvalidadoyfallodeByteTensorRNGregistrados;replay5000pasosporsemillaV185fueexactoenV186. No subagentes/ChatRelay/mensajería. Mantener6CPU,BelowNormal,concurrenciasensata.
'''
    (BASE/'handoff_codex/ESTADO_20261115_V186.md').write_text(handoff,encoding='utf-8')
    start=BASE/'INICIO_INVESTIGACION_CIENTIFICA.md'
    backup=BASE/'handoff_codex/backups_V186';backup.mkdir(exist_ok=False)
    shutil.copy2(start,backup/start.name)
    start.write_text('# Estado actual V186\n\nObjetivo activo,CT2histórico61sinincremento. Resultados y límites: [handoffV186](handoff_codex/ESTADO_20261115_V186.md). Manuscrito [V186](docs/TFM_MANUSCRITO_TRABAJO_V186.md).\n\n'+start.read_text(encoding='utf-8'),encoding='utf-8')
    goal=BASE/'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md'
    shutil.copy2(goal,backup/goal.name)
    goal.write_text(goal.read_text(encoding='utf-8')+'\n\n## Ampliación explícita del investigador,15/11/2026\n\nInvestigar también si puede haber grokking colectivo entre varios elementos y no solo dentro de una IA. Elegir cada siguiente paso por su capacidad de aproximar una aportación2/3,con razonamiento y simulaciones suficientes. La identidad social del mecanismo requiere controles frente a generalización individual. La advertencia histórica sobre remoto equivocado ya fue auditada:origin GalexY3/Metodologia-AB es el repositorio autorizado por este objetivo.\n',encoding='utf-8')
    print(json.dumps(evaluation),flush=True)


if __name__=='__main__':
    main()
