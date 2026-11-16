"""Registered decision audit and post hoc mechanistic figures; no fitting learner."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from v203_exact_gradient import initial,to_v202_probabilities
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
F=B/'results/V204_LOLA_NET_RETURN'


def main():
    receipt=json.loads((B/'V204_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,digest in receipt['source_sha256'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    raw=json.loads((F/'SUMMARY.json').read_text(encoding='utf-8'));rows=raw['rows']
    expected=[('COLD',None),('WARM',None)]+[('JITTER',2031600+i) for i in range(8)]
    assert [(r['kind'],r['seed']) for r in rows]==expected
    assert all(r['status']=='SUCCESS' for r in rows)
    table=[];precisions=[];maximum_logit=0.
    for r in rows:
        stem=f"{r['kind']}_{r['seed']}_LOLA";arr=np.load(F/f'{stem}.npz')
        assert arr['logits'].shape==(83,4,15,2,2) and arr['times'][-1]==6000
        assert np.array_equal(arr['logits'][0],initial(r['kind'],r['seed']))
        assert np.isfinite(arr['logits']).all()
        maximum_logit=max(maximum_logit,float(np.max(np.abs(arr['logits']))))
        e=r['snapshots'][-1]['native_evaluation'];br=r['snapshots'][-1]['public_deviations']
        stable=bool(e['functional'] and br['max_normalized_gain']<=.01)
        assert stable==r['snapshots'][-1]['stable_functional']
        table.append(dict(case=stem,kind=r['kind'],seed=r['seed'],functional=e['functional'],stable_functional=stable,
            GOOD=e['discounted_GOOD_joint_rate'],minimum_private_gain=min(e['gain_over_autarky']),
            payment_disable_effect=e['payment_disable_effect'],maximum_public_regret=br['max_normalized_gain']))
        if r['kind'] in ['COLD','WARM']:
            precise=np.load(F/f'{stem}_PRECISION.npz')['logits']
            error=float(np.max(np.abs(to_v202_probabilities(arr['logits'][-1])-to_v202_probabilities(precise[-1]))))
            assert error<=1e-4 and abs(error-r['precision_native_probability_max_error'])<1e-15
            precisions.append(error)
    assert maximum_logit<=12.001
    hits=sum(r['stable_functional'] for r in table if r['kind']=='JITTER')
    h1='PASS' if table[0]['stable_functional'] and hits>=6 else 'FAIL'
    assert h1==raw['H1']
    node=json.loads((B/'results/V204_NODE_INDEPENDENT_AUDIT.json').read_text(encoding='utf-8'))
    assert node['status']=='PASS' and node['cases']==42 and node['public_best_response_checks']==48
    cert=json.loads((B/'results/V204_CLOSED_FORM_CERTIFICATE.json').read_text(encoding='utf-8'))
    assert cert['status']=='PASS' and cert['n4_cross_component_checks']==57
    synthesis=dict(study='V204',status='REGISTERED_LOLA_ACQUISITION_FAIL',H1=h1,
        registration_commit=receipt['registration_commit'],registered_sources_preserved=True,
        main_deterministic_flows=10,precision_repeats=2,independent_worlds=0,
        no_agreement_functional=sum(r['functional'] for r in table if r['kind']!='WARM'),
        no_agreement_stable_functional=sum(r['stable_functional'] for r in table if r['kind']!='WARM'),
        no_agreement_cases=9,warm_functional=table[1]['functional'],warm_stable_functional=table[1]['stable_functional'],
        maximum_precision_probability_error=max(precisions),maximum_absolute_saved_logit=maximum_logit,
        node_audit={k:v for k,v in node.items() if k!='checked'},
        posthoc_closed_form=dict(components=57,maximum_relative_error=cert['maximum_relative_cross_error'],
            own_cost_power_epsilon_zero_n4=4,LOLA_cross_power_uniform_low_q_epsilon_zero_n4=8,
            eta20_cross_over_direct_at_actual_cold_point=cert['initial_epsilon20_ratio'],
            novel_priority_or_external_confirmation=False),
        new_N1_awards=[],CT2_historical=61,new_branch_score=None,N2=0,N3=0,overall_goal='ACTIVE',table=table)
    out=B/'results/V204_SCIENTIFIC_SYNTHESIS.json';assert not out.exists()
    out.write_text(json.dumps(synthesis,indent=2),encoding='utf-8')
    base=json.loads((B/'results/V203_EXACT_GRADIENT_FLOWS/SUMMARY.json').read_text(encoding='utf-8'))['rows']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(10.5,4),layout='constrained')
    for ax,kind in zip(axs,['COLD','WARM']):
        old=next(r for r in base if r['kind']==kind and not r['natural'])
        new=next(r for r in rows if r['kind']==kind)
        for r,label,color,marker in [(old,'Gradiente propio EPG','#3276a6','o'),(new,'LOLA exacto neto','#b75939','x')]:
            ax.plot([s['time'] for s in r['snapshots']],
                [s['native_evaluation']['discounted_GOOD_joint_rate'] for s in r['snapshots']],
                marker=marker,label=label,color=color)
        ax.set_xscale('symlog',linthresh=1);ax.set_xticks([0,60,600,6000],['0','60','600','6000'])
        ax.set_xlabel('Tiempo de optimización (no rondas)');ax.set_ylabel('GOOD conjunto nativo')
        ax.set_title('Inicio sin acuerdo' if kind=='COLD' else 'Acuerdo suministrado');ax.grid(alpha=.2)
    axs[0].set_yscale('log');axs[0].legend(fontsize=9);axs[1].set_ylim(0,.45)
    fig.suptitle('V204: LOLA no adquiere en los 9 puntos sin acuerdo; conserva WARM')
    fig.savefig(B/'results/FIG_V204_LOLA_VS_EPG.png',dpi=170);plt.close(fig)
    probe=json.loads((B/'results/V204_POSTHOC_GRADIENT_DECOMPOSITION.json').read_text(encoding='utf-8'))['rows']
    q=np.array([r['q'] for r in probe]);direct=np.array([-r['direct_payment_logit_direction'][0] for r in probe])
    cross=20*np.array([r['unscaled_LOLA_payment_correction'][0] for r in probe])
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.2),layout='constrained')
    axs[0].loglog(q,direct,'o-',label='Coste directo |D|; orden q⁴',color='#b75939')
    axs[0].loglog(q,cross,'s-',label='Término favorable 20 C; orden q⁸',color='#3276a6')
    axs[0].set_ylabel('Magnitud direccional de logits de pago');axs[0].legend(fontsize=8)
    axs[1].loglog(q,cross/direct,'o-',color='#3276a6');axs[1].axhline(1,color='gray',ls=':')
    axs[1].set_ylabel('20 C / |D|');axs[1].set_ylim(1e-13,2)
    for ax in axs:ax.set_xlabel('Probabilidad uniforme de participar q');ax.grid(alpha=.2,which='both')
    fig.suptitle('Diagnóstico posterior: la enseñanza se atenúa más que su coste\nSin exploración, n=4, pagos 1/2, pagador L=1; puntos de campo, no trayectorias',fontsize=12)
    fig.savefig(B/'results/FIG_V204_PAYMENT_GRADIENT_ORDERS.png',dpi=170);plt.close(fig)
    print(json.dumps({k:v for k,v in synthesis.items() if k not in ['table','node_audit']},indent=2))


if __name__=='__main__':
    apply_limits(2)
    main()
