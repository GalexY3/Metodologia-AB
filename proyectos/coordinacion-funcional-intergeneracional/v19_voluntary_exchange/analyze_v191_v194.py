"""Audit registered outcomes and produce inspectable scientific figures."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
R=B/'results'


def read(relative):return json.loads((R/relative).read_text(encoding='utf-8'))


def time_at(history,field,threshold):
    streak=0
    for row in history:
        streak=streak+1 if row[field]>=threshold else 0
        if streak==5:return row['step']
    return None


def main():
    output=R/'V191_V194_FINAL_AUDIT.json';assert not output.exists()
    s192=read('V192_DUAL_NEURAL_LEARNING/SUMMARY.json')
    s193=read('V193_FROZEN_PEER/SUMMARY.json');s194=read('V194_ORACLE_BANDIT/SUMMARY.json')
    audits=[read('V192_NUMPY_FINAL_AUDIT.json'),read('V193_V194_NUMPY_FINAL_AUDIT.json')]
    assert all(not d['failures'] for d in audits)
    keys={(c['family'],c['seed'],c['step'],c['field']) for d in audits for a in d['audits'] for c in a['checks']}
    assert len(keys)==192
    source_checks=[]
    for v in [192,193,194]:
        receipt=read(f'V{v}_PREREG_RECEIPT.json');assert receipt['before_training'] and receipt['remote_commit']
        for path,sha in receipt['source_sha256'].items():
            assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha,path
            source_checks.append(dict(registration=v,path=path,sha256=sha,unchanged=True))
    groups={}
    for family in ['ORACLE_FULL','PRIVATE_FULL','PRIVATE_BANDIT_IS']:
        groups[family]=[read(f'V192_DUAL_NEURAL_LEARNING/{family}/metrics_s{s}.json') for s in range(192115,192119)]
    groups['ORACLE_BANDIT_IS']=[read(f'V194_ORACLE_BANDIT/metrics_s{s}.json') for s in range(192115,192119)]
    decomposition=[]
    for family,rows in groups.items():
        for d in rows:
            h=d['history'];assert len(h)==600 and h[-1]['step']==60000
            assert d['t_mem']==time_at(h,'train_joint_greedy',.99)
            assert d['t_gen']==time_at(h,'test_joint_greedy',.95)
            if 'delayed_joint_generalization_candidate' in d:
                tm=d['t_mem'];tg=d['t_gen']
                expected=tm is not None and tg is not None and tg>=5*tm and tg-tm>=2000 and d['final']['train_joint_greedy']>=.99 and d['final']['test_joint_greedy']>=.95
                assert d['delayed_joint_generalization_candidate']==expected
            if family=='PRIVATE_FULL':
                for row in h:
                    ha=np.array(row['test_error_histograms'][0]);hb=np.array(row['test_error_histograms'][1])
                    g=row['train_chosen_gauge_A'];product=ha[g]*hb[(-g)%31]
                    cancellation=sum(ha[k]*hb[(-k)%31] for k in range(31) if k!=g)
                    assert abs(product+cancellation-row['test_joint_greedy'])<1e-12
                    decomposition.append(dict(seed=d['seed'],step=row['step'],local_correct_product=float(product),
                                               off_gauge_cancellation=float(cancellation),joint=row['test_joint_greedy']))
    frozen={arm:[read(f'V193_FROZEN_PEER/{arm}/metrics_s{s}.json') for s in range(192115,192119)] for arm in ['FREEZE_A','FREEZE_B']}
    for arm,rows in frozen.items():
        for d in rows:
            field='test_A' if d['active_role']==0 else 'test_B'
            assert d['t_gen_active']==time_at(d['history'],field,.95)
            assert len(d['history'])==588
            for row in d['history']:assert row['test_joint_greedy']<=row['joint_test_upper_bound_from_frozen_peer']+1e-12
    means={family:float(np.mean([d['final']['test_joint_greedy'] for d in rows])) for family,rows in groups.items()}
    # The numeric difference-in-differences is posthoc and descriptive. The
    # V194 prospective criterion was capability, not this numeric interaction.
    interactions=[]
    for i in range(4):
        y={family:rows[i]['final']['test_joint_greedy'] for family,rows in groups.items()}
        interactions.append((y['PRIVATE_FULL']-y['PRIVATE_BANDIT_IS'])-(y['ORACLE_FULL']-y['ORACLE_BANDIT_IS']))
    late={family:sum(d.get('delayed_joint_generalization_candidate',False) for d in rows) for family,rows in groups.items()}
    assert late['PRIVATE_FULL']==s192['delayed_candidate_counts']['PRIVATE_FULL']
    assert late['PRIVATE_BANDIT_IS']==s192['delayed_candidate_counts']['PRIVATE_BANDIT_IS']
    summary=dict(source_checks=source_checks,unique_numpy_metric_checks=len(keys),
        max_numpy_error=max(d['max_error'] for d in audits),means_test=means,
        V192_private_full_late_candidates=late['PRIVATE_FULL'],V192_private_bandit_late_candidates=late['PRIVATE_BANDIT_IS'],
        V193_active_local_passes=s193['active_local_pass_counts'],
        V193_all24saved_active_models_and_optimizers_match_joint_bitwise=True,
        V194_oracle_bandit_capability_count=s194['positive_control_count'],
        descriptive_feedback_by_partner_origin_interaction=interactions,
        mean_descriptive_interaction=float(np.mean(interactions)),
        interaction_numeric_threshold_not_preregistered=True,
        joint_test_decomposition_rows=len(decomposition),
        root_seed_context_blocks=4,V192_pair_histories=12,V193_counterfactual_continuations=8,V194_pair_histories=4,
        independent_external_scientific_confirmation=False,
        intrinsic_collective_grokking_accredited=False,institution_learning_accredited=False,
        N1='NOT_AUDITED',new_original_N1_awarded=False,N2=0,N3=0,CT2_historical=61,new_branch_score=None,
        canonical_score_sha256=hashlib.sha256((R/'AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest())
    assert summary['canonical_score_sha256']=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    assert s193['ongoing_coadaptation_necessity_refuted'] and s194['bandit_component_competence_passed']
    assert audits[1]['all_active_saved_models_match_joint_bitwise'] and audits[1]['all_active_saved_optimizers_match_joint_bitwise']
    output.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (R/'V192_JOINT_TEST_DECOMPOSITION.json').write_text(json.dumps(decomposition,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axs=plt.subplots(2,2,figsize=(12,8),sharex=True,sharey=True,layout='constrained')
    for i,origin in enumerate(['ORACLE','PRIVATE']):
        for j,feedback in enumerate(['FULL','BANDIT_IS']):
            family=origin+'_'+feedback;rows=groups[family];ax=axs[i,j]
            x=[r['step'] for r in rows[0]['history']]
            for field,color,label in [('train_joint_greedy','#0072B2','Entrenamiento'),('test_joint_greedy','#D55E00','Test')]:
                values=np.array([[r[field] for r in d['history']] for d in rows])
                for values_i in values:ax.plot(x,values_i,color=color,alpha=.16,lw=.7)
                ax.plot(x,values.mean(0),color=color,lw=2,label=label)
            ax.axhline(1/31,color='gray',ls=':',lw=1)
            ax.set(title=('Interlocutor correcto' if origin=='ORACLE' else 'Interlocutor que aprende')+' · '+('FULL' if feedback=='FULL' else 'binario'),ylim=(0,1.04))
            if j==0:ax.set_ylabel('Precisión conjunta codiciosa')
            if i==1:ax.set_xlabel('Actualizaciones')
            if i==j==0:ax.legend(loc='lower right')
    fig.savefig(R/'FIG_V192_V194_FEEDBACK_FACTORIAL.png');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4.8),sharey=True,layout='constrained')
    for j,arm in enumerate(['FREEZE_A','FREEZE_B']):
        rows=frozen[arm];ax=axs[j];role=rows[0]['active_role'];field='test_A' if role==0 else 'test_B'
        x=[r['step'] for r in rows[0]['history']]
        active=np.array([[r[field] for r in d['history']] for d in rows])
        joint=np.array([[r['test_joint_greedy'] for r in d['history']] for d in rows])
        original=np.array([[r[field] for r in d['history'] if r['step']>=1300] for d in groups['PRIVATE_FULL']])
        ax.plot(x,active.mean(0),color='#009E73',lw=3,label='Red activa; compañero congelado')
        ax.plot(x,original.mean(0),color='black',ls='--',lw=1.2,label='Misma red; ambos aprenden')
        ax.plot(x,joint.mean(0),color='#D55E00',lw=1.8,label='Par con compañero congelado')
        ax.set(title='Congelar '+('A' if j==0 else 'B'),xlabel='Paso total',ylim=(0,1.04))
        ax.text(.98,.45,'12/12 checkpoints: pesos y\nmomentos activos idénticos',transform=ax.transAxes,ha='right',fontsize=10)
    axs[0].set_ylabel('Precisión en test');axs[0].legend(loc='lower right',fontsize=9)
    fig.savefig(R/'FIG_V193_FROZEN_PEER_CAUSAL.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.7),layout='constrained')
    x=sorted({r['step'] for r in decomposition})
    for field,color,label in [('joint','#222222','Test conjunto'),('local_correct_product','#0072B2','Ambos aciertan su función local'),('off_gauge_cancellation','#D55E00','Compensación entre errores locales')]:
        y=[np.mean([r[field] for r in decomposition if r['step']==step]) for step in x]
        ax.plot(x,y,color=color,lw=2,label=label,ls='--' if field=='local_correct_product' else '-')
    ax.set(xlabel='Actualizaciones',ylabel='Fracción de pares de test',ylim=(0,1.04),title='V192 PRIVATE_FULL: descomposición exacta del resultado conjunto')
    ax.legend(loc='center right',fontsize=9)
    fig.savefig(R/'FIG_V192_JOINT_DECOMPOSITION.png');plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k!='source_checks'}),flush=True)


if __name__=='__main__':print('LIMITS',apply_limits(2),flush=True);main()
