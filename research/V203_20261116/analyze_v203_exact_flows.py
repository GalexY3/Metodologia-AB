"""Audit/summarize the completed registered oracle control; no new fitting."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_resource_limits import apply_limits
from v203_exact_gradient import history_spread, to_v202_probabilities

B=Path(__file__).resolve().parent
F=B/'results/V203_EXACT_GRADIENT_FLOWS'


def main():
    raw=json.loads((F/'SUMMARY.json').read_text(encoding='utf-8'))
    receipt=json.loads((B/'V203_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,digest in receipt['source_sha256'].items():
        assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    rows=raw['rows'];assert len(rows)==20 and not list(F.glob('*FAILED.json'))
    table=[];max_abs=0;max_cold_npg_mode=0;max_cold_npg_pay=0
    for row in rows:
        stem=f"{row['kind']}_{row['seed']}_{'NPG' if row['natural'] else 'EPG'}"
        data=np.load(F/f'{stem}.npz');states=data['logits']
        assert states.shape==(83,4,15,2,2),states.shape
        assert data['times'][0]==0 and data['times'][-1]==6000 and np.isfinite(states).all()
        max_abs=max(max_abs,float(np.max(np.abs(states))))
        e=row['snapshots'][-1]['native_evaluation']
        table.append(dict(case=stem,kind=row['kind'],natural=row['natural'],functional=e['functional'],
            GOOD=e['discounted_GOOD_joint_rate'],minimum_private_gain=min(e['gain_over_autarky']),
            payment_disable_effect=e['payment_disable_effect'],
            max_public_regret=row['snapshots'][-1]['public_deviations']['max_normalized_gain'],
            precision_probability_error=row.get('precision_native_probability_max_error')))
        if row['kind']=='COLD' and row['natural']:
            spreads=np.array([history_spread(x) for x in states])
            max_cold_npg_mode=float(spreads[:,0].max());max_cold_npg_pay=float(spreads[:,1].max())
        if 'precision_run' in row:
            precise=np.load(F/f'{stem}_PRECISION.npz')['logits']
            error=float(np.max(np.abs(to_v202_probabilities(states[-1])-to_v202_probabilities(precise[-1]))))
            assert abs(error-row['precision_native_probability_max_error'])<1e-15
            assert row['precision_endpoint_within_registered_tolerance'] and error<=1e-4
    assert max_abs<=12.001
    node=json.loads((B/'results/V203_NODE_INDEPENDENT_AUDIT.json').read_text(encoding='utf-8'))
    assert node['status']=='PASS' and node['cases']==84 and node['public_best_response_checks']==96
    cold=[x for x in table if x['kind']!='WARM'];warm=[x for x in table if x['kind']=='WARM']
    assert len(cold)==18 and len(warm)==2
    synthesis=dict(study='V203',status='COMPLETE_REGISTERED_NEGATIVE_ACQUISITION',
        registration_commit=receipt['registration_commit'],registered_sources_preserved=True,
        deterministic_flows=20,precision_repeats=4,scientific_world_replicates=0,
        no_agreement_prior_functional=sum(x['functional'] for x in cold),no_agreement_prior_cases=18,
        supplied_agreement_functional=sum(x['functional'] for x in warm),supplied_agreement_cases=2,
        precision_all_four_pass=True,max_precision_probability_error=max(x['precision_probability_error'] or 0 for x in table),
        maximum_abs_saved_logit=max_abs,cold_NPG_history_mode_spread_all_checkpoints=max_cold_npg_mode,
        cold_NPG_history_payment_spread_all_checkpoints=max_cold_npg_pay,
        independent_language_audit={k:v for k,v in node.items() if k!='checked'},
        interpretation='This exact oracle-gradient control does not acquire from the specified cold neighborhood. It improves an externally supplied viable agreement. It does not prove universal impossibility or original sociological law.',
        V202_H1_unchanged='FAIL',external_scientific_confirmation=False,CT2_historical=61,
        new_branch_score=None,new_N1_awards=[],N2=0,N3=0,table=table)
    target=B/'results/V203_SCIENTIFIC_SYNTHESIS.json';assert not target.exists()
    target.write_text(json.dumps(synthesis,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(11.6,7.5),layout='constrained')
    colors={('COLD',False):'#b34b39',('COLD',True):'#d99c20',('WARM',False):'#2476a6',('WARM',True):'#268268'}
    for row in rows:
        if row['kind']=='JITTER':continue
        label=f"{'Sin acuerdo' if row['kind']=='COLD' else 'Acuerdo suministrado'} / {'natural' if row['natural'] else 'euclídeo'}"
        x=[s['time'] for s in row['snapshots']];color=colors[row['kind'],row['natural']]
        es=[s['native_evaluation'] for s in row['snapshots']]
        ys=[[e['discounted_GOOD_joint_rate'] for e in es],
            [min(e['gain_over_autarky']) for e in es],
            [e['payment_disable_effect'] for e in es],
            [s['public_deviations']['max_normalized_gain'] for s in row['snapshots']]]
        for ax,yv in zip(axes.flat,ys):ax.plot(x,yv,'o-',color=color,label=label,markersize=5)
    titles=['Producción GOOD conjunta','Ganancia privada mínima frente a AUTO',
        'Caída de GOOD al deshabilitar pagos','Ganancia máxima de una desviación pública']
    for ax,title in zip(axes.flat,titles):
        ax.set_title(title);ax.set_xscale('symlog',linthresh=1);ax.set_xlabel('Tiempo de optimización (no rondas sociales)');ax.grid(alpha=.2)
        ax.set_xticks([0,60,600,6000],['0','60','600','6000'])
    axes[0,0].set_ylim(0,.45);axes[0,0].axhline(.20,ls=':',color='gray')
    axes[0,1].axhline(.02,ls=':',color='gray');axes[1,0].axhline(.10,ls=':',color='gray')
    axes[1,1].set_yscale('log');axes[1,1].set_ylim(1e-6,1)
    axes[0,0].legend(fontsize=8,loc='upper left')
    fig.suptitle('V203: adquisición ausente; mejora del acuerdo proporcionado\nControl oracular determinista, 4 checkpoints; las 8 perturbaciones por campo tampoco adquieren',fontsize=13)
    fig.savefig(B/'results/FIG_V203_EXACT_GRADIENT_FLOWS.png',dpi=170)
    plt.close(fig)
    print(json.dumps({k:v for k,v in synthesis.items() if k not in ['table','interpretation','independent_language_audit']},indent=2))


if __name__=='__main__':
    apply_limits(2)
    main()
