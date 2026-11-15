"""Recompute consequential claims, preserve failures, and build scientific figures."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import scipy
import numba
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_resource_limits import apply_limits
from v178_private_affine_rival import generation,MODES

ROOT=Path(__file__).resolve().parent
CHECKS=[]


def read(name):return json.loads((ROOT/name).read_text(encoding='utf8'))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(name,condition,detail=None):
    assert condition,(name,detail)
    CHECKS.append(dict(name=name,passed=True,detail=detail))


def write(name,content):
    p=ROOT/name;data=content.encode('utf8') if isinstance(content,str) else content
    if p.exists():assert p.read_bytes()==data,('Preserve previous output',name)
    else:p.write_bytes(data)


def js(name,obj):write(name,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def main():
    limits=apply_limits(3)
    v175=read('results/v175_learned_memory/SUMMARY.json');v176=read('results/v176_frozen_memory/SUMMARY.json')
    v177=read('results/v177_gate_game/SUMMARY.json');v178=read('results/v178_private_affine_M5/SUMMARY.json')
    v179=read('results/V179_HUMAN_POINT_AND_RANDOMIZATION_REPLICATION.json')
    v180=read('results/v180_open_policy_space/MAINTENANCE.json');val=read('results/v180_open_policy_space/VALIDATION.json')
    freeze175=v175['freeze'];freeze178=v178['freeze'];freeze180=read('results/v180_open_policy_space/FREEZE.json')
    for name,freeze,source,protocol in (
        ('V175',freeze175,'v175_memory_evolution.py','PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md'),
        ('V178',freeze178,'v178_private_affine_rival.py','PREREG_V178_PRIVATE_AFFINE_RIVAL.md'),
        ('V180',freeze180,'v180_open_policy_space.py','PREREG_V180_OPEN_POLICY_SPACE.md')):
        check(name+'_source_frozen',sha(ROOT/source)==freeze['source_sha256'])
        check(name+'_protocol_frozen',sha(ROOT/protocol)==freeze['protocol_sha256'])
        check(name+'_remote_prereg_recorded',len(freeze['prereg_commit'])==40,freeze['prereg_commit'])
    for item in v175['results']:
        path=f"results/v175_learned_memory/{item['mode']}_{item['seed']}"
        curve=read(path+'/CURVE.json')
        check('V175_complete_'+str(item['seed'])+'_'+item['mode'],len(curve)==3000 and curve[-1]['generation']==3000)
        check('V175_tail_'+str(item['seed'])+'_'+item['mode'],float(np.mean([r['Q'] for r in curve[-500:]]))==item['Q_tail'])
        check('V175_resource_limits_'+str(item['seed'])+'_'+item['mode'],item['resource_limits']['priority']=='BelowNormal' and item['resource_limits']['affinity']==16515072 and item['resource_limits']['numba_threads']==3)
        check('V175_checkpoints_'+str(item['seed'])+'_'+item['mode'],len(list((ROOT/path).glob('CHECKPOINT_*.npz')))==6)
    check('V175_both_primary_capacity_fail',all(not t['generic_memory_capacity'] for t in v175['tests'].values()))
    check('V175_both_full_rnn_diagnostic_fail',all(not t['diagnostic_full_rnn_capacity'] for t in v175['tests'].values()))
    check('V176_prespecified_recurrence_pass',v176['tests']['recurrence_necessary_in_both'])
    check('V176_no_sensory_independence',not v176['tests']['no_variable_sensory_capacity_in_both'])
    for row in v176['results']:
        name=f"results/v176_frozen_memory/{row['mode']}_{row['seed']}_M{row['m']}.json"
        raw=read(name)['groups']
        for condition,batches in raw.items():
            fit=np.concatenate([np.asarray(b['fit']) for b in batches]);q=fit.sum(1)
            check('V176_recomputed_'+row['mode']+'_'+str(row['seed'])+'_M'+str(row['m'])+'_'+condition,
                  abs(q.mean()-row['means'][condition]['Q'])<1e-12)
        if row['mode'] in ('LINEAR_FULL','MLP_RESOURCE'):
            check('V176_neutral_reset_'+row['mode']+'_'+str(row['seed'])+'_M'+str(row['m']),row['means']['INTACT']==row['means']['RESET'])
    for row in v177['results']:
        dat=np.load(ROOT/f"results/v177_gate_game/{row['mode']}_{row['seed']}_PAYOFFS.npz")
        pay=dat['payoffs'];regret=np.zeros((len(pay),32))
        for mask in range(32):
            gain=np.stack([pay[:,mask^(1<<i),i]-pay[:,mask,i] for i in range(5)],axis=1)
            regret[:,mask]=np.maximum(0,gain.max(1))
        check('V177_full_payoff_reaudit_'+row['mode']+'_'+str(row['seed']),np.array_equal(regret,dat['regret']))
        check('V177_all_on_Q_'+row['mode']+'_'+str(row['seed']),float(pay[:,31,:].sum(1).mean())==row['Q_all_on'])
        change=pay[:,0,:]-pay[:,31,:]
        trap=(regret[:,31]<=1e-10)&(change.min(1)>=-1e-10)&(change.max(1)>1e-10)
        check('V177_trap_'+row['mode']+'_'+str(row['seed']),float(trap.mean())==row['strong_trap_fraction'])
    check('V177_strong_trap_failed',not v177['strong_collective_trap_in_both'])
    for study,rows,directory in (
        ('V178',v178['results'],'results/v178_private_affine_M5'),
        ('V180',v180['results'],'results/v180_open_policy_space/maintenance')):
        for row in rows:
            label=row.get('mode',row.get('arm'));path=ROOT/f"{directory}/{label}_{row['seed']}"
            curve=read(str(path.relative_to(ROOT))+'/CURVE.json')
            check(study+'_complete_'+label+'_'+str(row['seed']),len(curve)==3000 and curve[-1]['generation']==3000)
            check(study+'_tail_'+label+'_'+str(row['seed']),float(np.mean([r['Q'] for r in curve[-500:]]))==row['Q_tail'])
            data=np.load(path/'FINAL_POPULATION.npz');mode=MODES[label] if study=='V178' else (0 if label=='LOCKED' else 3)
            replay=generation(data['theta'].reshape(100,5,3),data['y0'],mode)[0]
            check(study+'_exact_endpoint_'+label+'_'+str(row['seed']),np.array_equal(replay,data['fit']))
            check(study+'_six_checkpoints_'+label+'_'+str(row['seed']),len(list(path.glob('CHECKPOINT_*.npz')))==6)
            lim=row.get('resource_limits',row.get('limits'))
            check(study+'_limits_'+label+'_'+str(row['seed']),lim['priority']=='BelowNormal' and lim['affinity']==16515072 and lim['numba_threads']==3)
    check('V178_primary_failed',not v178['primary_gate'])
    check('V178_full_control_passed',v178['full_control_gate'])
    check('V178_M16_not_executed',not (ROOT/'results/v178_private_affine_M16').exists())
    check('V180_primary_failed',not v180['primary_gate'])
    check('V180_control_passed',v180['control_gate'])
    check('V180_destructive_bias_failed',not val['destructive_bias_in_all4'])
    check('V180_selection_hash',sha(ROOT/'results/v180_open_policy_space/SELECTION.json')==val['selection_sha256'])
    check('V180_selected_validation_positive',all(p['fitness_error']==0 and p['action_mismatches']==0 for p in val['original_source_parity']))
    check('V179_correct_clusters',v179['grain']['rows']==320 and v179['grain']['waterways']==160)
    check('V179_CI_reconstructed',all(r['ci_max_error']<1e-12 for r in v179['exact_export_checks']))
    check('V179_RI_reconstructed',all(r['p_one_sided_greater']==r['published_p_one_sided'] for r in v179['randomization']))
    contrast=next(r for r in v179['estimates'] if r['contrast']=='government_minus_public')
    check('V179_direct_difference_not_established',contrast['ci95'][0]<0<contrast['ci95'][1])
    check('V179_no_imputation_in_regression_variables',all(n==0 for n in v179['grain']['raw_missing_in_used_variables'].values()))
    old=read('results/V166_CROSS_CYCLE_TECHNICAL_AUDIT.json');preserved=0
    for r in old['checks']:
        if r.get('check')=='results_file_exists':
            check('prior_V166_hash_'+r['file'],sha(ROOT/'results'/r['file'])==r['sha256']);preserved+=1
    check('prior_V165_CI_miss_preserved',len(old['ci_misses'])==1)
    check('V169_original_not_changed',sha(ROOT/'v169_local_private_contract_learning.py')=='c92d27bbb531d432ad992660b8330d79599216316006224cf3d2ccb15df96c56')
    check('old_evidence_ZIP_not_changed',sha(ROOT/'research/V169_V174_20261115/EVIDENCE.zip')=='6fd744cde4f02af581e823b0bed2bdee7965a03f17ee7d24cfc61d1dbfed66b0')
    canonical=read('results/AB_PROGRESO_CT2_CT3.json')
    check('canonical_CT2_preserved',canonical['score_history'][-1]['proximity_2of3']==61 and canonical['N2']==0 and canonical['N3']==0)
    failures=[dict(study='V175',criterion='Generic private memory Q>=.70 in both seeds',outcome='failed2/2; full-information RNN diagnostic also failed2/2'),
              dict(study='V176',criterion='High capacity without variable sensory input',outcome='failed; recurrence helps private policies but does not remove need for private feedback'),
              dict(study='V177',criterion='Strong ex-post Pareto trap in >=50% groups in both full-RNN populations',outcome='failed:0% and4.296875%'),
              dict(study='V178',criterion='Affine private >=.70 in6/8 and median gain>=.20',outcome='failed0/8; M16 cancelled as preregistered'),
              dict(study='V180',criterion='Maintenance collapse in>=6/8',outcome='failed1/8; retained heterogeneity'),
              dict(study='V180',criterion='Common destructive profitable bias in four held-out populations',outcome='failed; minimax screen selected b=0'),
              dict(study='V179',criterion='Human government-public effect difference established',outcome='not established; contrast post hoc, CI95[-.09993,.48926]')]
    audit=dict(study='V175_V180_FINAL_POSTHOC_AUDIT',passed=len(CHECKS),checks=CHECKS,
               retained_scientific_failures=failures,checks_are_not_AB_cycles=True,evolution_runs=66,
               repeated_original_endpoints=56,V175_endpoints_previously_replayed=10,
               limits=limits,prior_raw_files_hash_verified=preserved,
               versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,numba=numba.__version__,matplotlib=matplotlib.__version__),
               external_scientific_confirmation=False,N2=0,CT2_historical_unchanged=61)
    audit_path='results/V175_V180_FINAL_AUDIT.json'
    if (ROOT/audit_path).exists():
        # Keep the original audit and its actual process metadata on re-render.
        prior=read(audit_path)
        assert {k:v for k,v in prior.items() if k!='limits'}=={k:v for k,v in audit.items() if k!='limits'}
    else:js(audit_path,audit)
    q175={name:[r['Q_tail'] for r in v175['results'] if r['mode']==name] for name in v175['freeze']['modes']}
    q178={name:[r['Q_tail'] for r in v178['results'] if r['mode']==name] for name in MODES}
    stats=dict(V175=q175,V178={k:dict(values=v,mean=float(np.mean(v)),sd=float(np.std(v,ddof=1)),min=min(v),max=max(v)) for k,v in q178.items()},
               V180=dict(paired=v180['paired'],open_above_point30=sum(r['Q']['OPEN']>.3 for r in v180['paired']),
                         open_above_point70=sum(r['Q']['OPEN']>=.7 for r in v180['paired']),
                         mean_locked=float(np.mean([r['Q']['LOCKED'] for r in v180['paired']])),
                         mean_open=float(np.mean([r['Q']['OPEN'] for r in v180['paired']]))),
               V176_M5=[dict(seed=r['seed'],mode=r['mode'],means=r['means'],contrasts=r['contrasts']) for r in v176['results'] if r['m']==5],
               V177=v177['results'],V179=v179['estimates'],retained_failures=failures)
    js('results/V175_V180_REVIEWED_STATISTICS.json',stats)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(12,8.5),layout='constrained')
    def points(ax,names,data,labels):
        for x,name in enumerate(names):
            vals=data[name];offset=np.linspace(-.10,.10,len(vals))
            ax.scatter(x+offset,vals,s=28,color='#267ca8',zorder=3)
            ax.hlines(np.mean(vals),x-.22,x+.22,color='#25313d',lw=2,zorder=2)
        ax.set_xticks(range(len(names)),labels);ax.set_ylim(-.025,1.025);ax.set_ylabel('Q: riqueza media total');ax.grid(axis='y',alpha=.18)
    points(axes[0,0],['RNN_RESOURCE','RNN_FULL','MLP_RESOURCE','LINEAR_FULL','FILTER_RESOURCE'],q175,
           ['RNN\nprivada','RNN\ncolectiva','MLP\nprivada','Lineal\ncolectiva','Filtro\nestructurado'])
    axes[0,0].axhline(.7,color='#b26438',ls='--',lw=1);axes[0,0].set_title('A. V175: dos evoluciones por arquitectura')
    for i,mode in enumerate(('RNN_RESOURCE','RNN_FULL')):
        for j,r in enumerate(r for r in v176['results'] if r['mode']==mode and r['m']==5):
            axes[0,1].plot([i*2,i*2+1],[r['means']['INTACT']['Q'],r['means']['RESET']['Q']],marker='o',lw=1.3,color=('#267ca8','#b26438')[j])
    axes[0,1].set_xticks([0,1,2,3],['Privada\nintacta','Privada\nsin memoria','Colectiva\nintacta','Colectiva\nsin memoria'])
    axes[0,1].set_ylim(-.025,1.025);axes[0,1].set_ylabel('Q en evaluación congelada');axes[0,1].grid(axis='y',alpha=.18)
    axes[0,1].set_title('B. V176: efecto causal de la recurrencia')
    points(axes[1,0],list(MODES),q178,['Colectiva\noriginal','Privada\noriginal','Privada\nafín','Colectiva\nafín','Umbral\nprivado'])
    axes[1,0].set_title('C. V178: ocho evoluciones; el rival afín falla')
    for r in v180['paired']:
        axes[1,1].plot([0,1],[r['Q']['LOCKED'],r['Q']['OPEN']],color='#267ca8',alpha=.75,marker='o',lw=1)
    axes[1,1].scatter(np.full(8,2),q178['AFFINE_FULL'],marker='s',color='#b26438',s=25)
    axes[1,1].axhline(.3,color='#68717a',ls='--',lw=.8)
    axes[1,1].set_xticks([0,1,2],['Ya formada:\nintercepto neutral','Ya formada:\nintercepto activo','Desde cero:\nintercepto activo'])
    axes[1,1].set_ylim(-.025,1.025);axes[1,1].set_ylabel('Q de últimas 500 generaciones');axes[1,1].grid(axis='y',alpha=.18)
    axes[1,1].set_title('D. V180: formación y mantenimiento difieren')
    fig.suptitle('Capacidad, uso de memoria e historia de formación',fontsize=14)
    fig.text(.5,-.025,'Puntos: evoluciones. Barras horizontales: medias. Líneas inclinadas: contrafactuales emparejados.\nV176 evalúa poblaciones congeladas. Q no es porcentaje de cooperación. Ningún panel acredita una institución humana.',ha='center',fontsize=9)
    target=ROOT/'results/FIG_V175_V180_CORE.png';fig.savefig(target,dpi=220,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained')
    for j,r in enumerate(v179['estimates']):
        ax.errorbar(r['estimate'],2-j,xerr=[[r['estimate']-r['ci95'][0]],[r['ci95'][1]-r['estimate']]],fmt='o',color=('#267ca8','#267ca8','#b26438')[j],capsize=4,lw=2)
    ax.axvline(0,color='#555d64',lw=1);ax.set_yticks([2,1,0],['Información al gobierno','Información al público','Diferencia gobierno−público'])
    ax.set_xlabel('Efecto sobre índice de calidad del agua (mayor = mejor); IC 95% CR2')
    ax.set_title('V179: reproducir un ensayo humano no confirma el simulador')
    ax.text(.02,-.27,'160 vías de agua, dos auditorías por vía. Contraste directo: p=.189.\nReanálisis de Buntaine et al. (2021); sin nueva muestra ni institución aprendida.',transform=ax.transAxes,fontsize=9)
    target=ROOT/'results/FIG_V179_HUMAN_MONITORING.png';fig.savefig(target,dpi=220,bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
    for ax,bounds,title in zip(axes,[(0,100),(60,62)],['Escala completa 0–100','Vista ampliada 60–62']):
        ax.plot(range(7),[61]*7,'o-',color='#267ca8');ax.set_ylim(*bounds)
        ax.set_xticks(range(7),['V174','V175','V176','V177','V178','V179','V180'],rotation=30)
        ax.set_title(title);ax.set_ylabel('CT2 histórico conservado');ax.grid(axis='y',alpha=.18)
    fig.suptitle('Proximidad ordinal sin aumento: 61/100; N2=N3=0',fontsize=12)
    target=ROOT/'results/FIG_CT2_V175_V180.png';fig.savefig(target,dpi=200,bbox_inches='tight');plt.close(fig)
    js('results/AB_EVALUACION_V175_V180_20261115.json',dict(method='AB3.2.1',date='2026-11-15',
          canonical_branch_id=canonical['branch_id'],canonical_CT2_historical=61,new_ecological_branch_score=None,
          N1='NOT_AUDITED',N2=0,N3=0,no_score_increase=True,
          rationale='Failed high-capacity memory, Pareto-trap, affine-private, maintenance-collapse and destructive-invasion gates; human direct contrast inconclusive. Reproducibility and TFM improved, independent novel prediction not confirmed.',
          technical_audit='results/V175_V180_FINAL_AUDIT.json',scientific_failures=failures,
          goal_status='active; excellent TFM and original contribution still require work'))
    print('V175_V180_AUDIT',len(CHECKS),'passed;66evolutions;7retained scientific failures',flush=True)
    print('V178_REVIEWED',json.dumps(stats['V178']),flush=True)
    print('V180_REVIEWED',json.dumps(stats['V180']),flush=True)


if __name__=='__main__':main()
