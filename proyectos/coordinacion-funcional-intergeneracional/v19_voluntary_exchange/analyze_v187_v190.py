"""Prespecified gate audit, descriptive summaries and static scientific figures."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
R=B/'results'


def read(path):return json.loads((R/path).read_text(encoding='utf-8'))


def gate_time(history,predicate):
    count=0
    for row in history:
        count=count+1 if predicate(row) else 0
        if count==5:return row['step']
    return None


def main():
    assert (R/'V188_V190_NUMPY_FINAL_AUDIT.json').exists()
    assert not (R/'V187_V190_FINAL_AUDIT.json').exists()
    classical=read('V187_CLASSICAL_SIGNALING/SUMMARY.json')
    old=read('V188_PRIVATE_CONVENTIONS/SUMMARY.json')
    new=read('V190_LOSSY_MEMORIZATION/SUMMARY.json')
    numeric=read('V188_V190_NUMPY_FINAL_AUDIT.json');assert not numeric['failures']
    source_checks=[]
    for v in [187,188,190]:
        reg=read(f'V{v}_PREREG_RECEIPT.json')
        timing_flag='before_campaign' if v==187 else 'before_training'
        assert reg[timing_flag] and reg['remote_commit']
        for path,sha in reg['source_sha256'].items():
            actual=hashlib.sha256((B/path).read_bytes()).hexdigest()
            assert actual==sha,path
            source_checks.append(dict(experiment=v,path=path,sha256=sha,unchanged=True))
    all190=[];residuals=[]
    for support in ['LOW','HIGH']:
        for family in ['FIXED_PROTOCOL','PRIVATE']:
            for seed in range(190115,190123):
                d=read(f'V190_LOSSY_MEMORIZATION/{support}_{family}/metrics_s{seed}.json')
                h=d['history'];assert len(h)==600 and h[-1]['step']==60000
                assert d['t_mem']==gate_time(h,lambda r:r['train']>=.99)
                assert d['t_gen']==gate_time(h,lambda r:r['test']>=.95)
                lossy=gate_time(h,lambda r:r['train']==1. and r['symbols']<31)
                assert d['t_mem_lossy']==lossy
                if support=='HIGH':assert lossy is None
                snapshot=R/f'V190_LOSSY_MEMORIZATION/{support}_{family}/first_lossy_memorization_s{seed}.pt'
                assert snapshot.exists()==(lossy is not None)
                tl=lossy;tg=d['t_gen'];f=d['final']
                candidate=family=='PRIVATE' and tl is not None and tg is not None and tg>=5*tl and tg-tl>=2000 and f['train']==1. and f['test']>=.95 and f['symbols']==31
                assert d['capacity_expanding_delayed_candidate']==candidate
                for r in h:
                    residuals.append(372*r['train_expected']+589*r['test_expected']-961*r['full_capacity_stochastic'])
                all190.append(d)
    assert max(residuals)<=.01
    candidates=[d for d in all190 if d['capacity_expanding_delayed_candidate']]
    positives={s:sum(d['final']['test']>=.95 for d in all190 if d['support']==s and d['family']=='FIXED_PROTOCOL') for s in ['LOW','HIGH']}
    primary=all(v>=6 for v in positives.values()) and len(candidates)>=4 and len({d['pair'] for d in candidates})>=2
    assert primary==new['primary_gate_passed']
    graph_checks=[]
    for pair in range(4):
        d=np.load(R/f'V189B_MATCHED_CONTEXTS/pair_{pair}.npz');lo=d['low'];hi=d['high']
        assert lo.dtype==bool and hi.dtype==bool
        assert lo.sum()==hi.sum()==372 and np.array_equal(lo,lo.T) and np.array_equal(hi,hi.T)
        for axis in [0,1]:assert np.all(lo.sum(axis)==12) and np.all(hi.sum(axis)==12)
        _,bb=np.indices((31,31));aa=np.indices((31,31))[0];yy=(aa+bb)%31
        assert np.array_equal(np.bincount(yy[lo],minlength=31),np.bincount(yy[hi],minlength=31))
        graphs=[]
        for mask in [lo,hi]:
            g=(mask.astype(int)@mask.astype(int).T)>0;np.fill_diagonal(g,False);graphs.append(g)
        color=d['low_oracle_dictionary'];assert len(np.unique(color))==16
        assert not np.any(graphs[0]&(color[:,None]==color[None,:]))
        assert all(graphs[0][a,b] or graphs[0][a,c] or graphs[0][b,c] for a,b,c in itertools.combinations(range(31),3))
        assert graphs[1].sum()==31*30
        graph_checks.append(dict(pair=pair,train=372,test=589,all_marginals_matched=True,
                                 low_coloring16_and_no_independent_triple=True,high_complete=True,
                                 low_oracle_train1_test_ceiling=124/589))
    def groups(ds,keys):
        answer=[]
        labels=sorted({tuple(d[k] for k in keys) for d in ds})
        for label in labels:
            rows=[d for d in ds if tuple(d[k] for k in keys)==label]
            answer.append(dict(zip(keys,label))|dict(n=len(rows),means={k:float(np.mean([d['final'][k] for d in rows])) for k in ['train','test','train_expected','test_expected']},
                    test_min=float(min(d['final']['test'] for d in rows)),test_max=float(max(d['final']['test'] for d in rows)),
                    reached_99_train=sum(d['t_mem'] is not None for d in rows),reached_95_test=sum(d['t_gen'] is not None for d in rows),
                    exact_final_train=sum(d['final']['train']==1. for d in rows),
                    lossy_mem_entries=sum(d.get('t_mem_lossy') is not None for d in rows),
                    max_observed_train_by_seed=[max(r['train'] for r in d['history']) for d in rows]))
        return answer
    oldfull=[read(f"V188_PRIVATE_CONVENTIONS/{d['family']}/metrics_s{d['seed']}.json") for d in old['runs']]
    diagnostics=[]
    for a in numeric['audits']:
        c=a['checks'][0];rows=a['reference_rows']
        diagnostics.append(dict(experiment=c['experiment'],support=c['support'],family=c['family'],n=len(rows),
                                receivers_at_code_training_ceiling=sum(r['receiver_attains_greedy_training_ceiling'] for r in rows),
                                senders_with_immediate_greedy_improvement=sum(r['sender_has_improving_greedy_deviation'] for r in rows),
                                maximum_correct_cases_gain=max(r['maximum_train_cases_gained_by_one_state_message_change'] for r in rows),
                                mean_oracle_train_given_code=float(np.mean([r['training_oracle_given_greedy_code'] for r in rows]))))
    summary=dict(V188_groups=groups(oldfull,['family']),V190_groups=groups(all190,['support','family']),
                 conditional_code_diagnostics=diagnostics,
                 V190_positive_counts=positives,V190_candidate_count=len(candidates),V190_primary=bool(primary),
                 V190_low_private_lossy_entries=sum(d['t_mem_lossy'] is not None for d in all190 if d['support']=='LOW' and d['family']=='PRIVATE'),
                 V190_context_pairs=4,neural_seeds_per_context_pair=2,
                 V190_capacity_evaluations=len(residuals),max_weighted_capacity_residual=float(max(residuals)),
                 source_checks=source_checks,graph_checks=graph_checks,
                 numpy_numeric_checks=numeric['numeric_checks'],numpy_max_error=numeric['max_error'],
                 canonical_progress_sha256=hashlib.sha256((R/'AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest(),
                 classical_known_effect_calibration=classical['competence_gate_passed'],
                 no_collective_grokking_accredited=True,no_new_N1_awarded=True,N2=0,N3=0,CT2_historical=61,new_branch_score=None)
    (R/'V187_V190_FINAL_AUDIT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axs=plt.subplots(1,2,figsize=(12,4.7),layout='constrained')
    for i,condition in enumerate(['PURE','LIMITED35']):
        vals=np.array([r['accuracy'] for r in classical['rows'] if r['condition']==condition])
        axs[0].scatter(i+np.linspace(-.13,.13,len(vals)),vals,s=12,alpha=.45)
        axs[0].plot([i-.2,i+.2],[vals.mean()]*2,color='black',lw=2)
    axs[0].set(xticks=[0,1],xticklabels=['Ilimitada','Limitada (35)'],ylim=(0,1.04),ylabel='Precisión comunicativa',title='V187: calibración clásica, 100 semillas')
    for i,family in enumerate(['FIXED_PROTOCOL','REINFORCE','URN_PURE','URN_LIMITED']):
        rows=[d for d in oldfull if d['family']==family];v=[d['final']['test'] for d in rows]
        axs[1].scatter(i+np.linspace(-.1,.1,8),v,s=28)
        axs[1].plot([i-.2,i+.2],[np.mean(v)]*2,color='black',lw=2)
    axs[1].axhline(.95,color='gray',ls=':',lw=1)
    axs[1].set(xticks=range(4),xticklabels=['Código\nfijo','REINFORCE','Urna\nilimitada','Urna\nlimitada'],ylim=(0,1.04),ylabel='Precisión en test',title='V188: adaptación neuronal, 8 semillas')
    fig.savefig(R/'FIG_V187_V188_CLASSICAL_TRANSFER.png');plt.close(fig)
    d=np.load(R/'V189B_MATCHED_CONTEXTS/pair_0.npz')
    fig,axs=plt.subplots(2,2,figsize=(9,8),layout='constrained')
    for j,(key,chi) in enumerate([('low',16),('high',31)]):
        m=d[key];g=(m.astype(int)@m.astype(int).T)>0;np.fill_diagonal(g,False)
        axs[0,j].imshow(m,cmap='Blues',vmin=0,vmax=1,interpolation='nearest');axs[0,j].set(title=f'{key.upper()}: 372 pares conocidos',xlabel='Contexto b',ylabel='Entrada a')
        axs[1,j].imshow(g,cmap='Greys',vmin=0,vmax=1,interpolation='nearest');axs[1,j].set(title=f'Grafo de confusión: χ={chi}',xlabel="Entrada a′",ylabel='Entrada a')
    fig.suptitle('Marginales a, b e y idénticos dentro de cada pareja')
    fig.savefig(R/'FIG_V189B_MATCHED_CONTEXTS.png');plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(12,8),sharex=True,sharey=True,layout='constrained')
    for i,support in enumerate(['LOW','HIGH']):
        for j,family in enumerate(['FIXED_PROTOCOL','PRIVATE']):
            ax=axs[i,j];rows=[d for d in all190 if d['support']==support and d['family']==family];x=[r['step'] for r in rows[0]['history']]
            for field,color,label in [('train','#0072B2','Entrenamiento'),('test','#D55E00','Test')]:
                y=np.array([[r[field] for r in d['history']] for d in rows])
                for yi in y:ax.plot(x,yi,color=color,alpha=.15,lw=.7)
                ax.plot(x,y.mean(0),color=color,lw=2,label=label)
            ax.axhline(.95,color='gray',ls=':',lw=.8);ax.set(title=f'{support} · '+('código fijo' if family=='FIXED_PROTOCOL' else 'código privado'),ylim=(0,1.04))
            if i==1:ax.set_xlabel('Actualizaciones')
            if j==0:ax.set_ylabel('Precisión codiciosa')
            if i==j==0:ax.legend(loc='lower right')
    fig.savefig(R/'FIG_V190_CONTEXT_TRAJECTORIES.png');plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['source_checks','graph_checks','V188_groups','V190_groups']}),flush=True)


if __name__=='__main__':print('LIMITS',apply_limits(2));main()
