"""Additive synthesis of completed, frozen V205 results; no primary reruns."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent


def read(name):return json.loads((B/name).read_text(encoding='utf-8'))


def main():
    target=B/'results/V205_SCIENTIFIC_SYNTHESIS.json';assert not target.exists()
    reg=read('V205_REGISTRATION_RECEIPT.json')
    for name,digest in reg['source_sha256'].items():
        assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    primary=read('results/V205_ADVALIGN_NASH_AUDIT/SUMMARY.json')
    literal=read('results/V205_ADVALIGN_NASH_AUDIT/LITERAL_FIELDS.json')
    authors=read('results/V205_ADVALIGN_NASH_AUDIT/AUTHOR_HELPERS.json')
    js=read('results/V205_NODE_INDEPENDENT_AUDIT.json')
    symbolic=read('results/V205_SYMBOLIC_CERTIFICATE.json')
    intervention=read('results/V205_POSTHOC_MARGINALIZATION.json')
    assert len(literal)==320 and len(authors)==144
    assert primary['H1']=='CONFIRMED_INTERNAL_COUNTEREXAMPLE'
    assert js['status']==symbolic['status']=='PASS'
    assert all(abs(r['initial']['max_gain'])<1e-12 for r in literal)
    zero=[r for r in literal if r['beta']==0 or r['advantages']=='marginal']
    zero_error=max(abs(x) for r in zero for row in r['field'] for x in row)
    assert zero_error<1e-12
    aa=[r for r in authors if r['loss_mode']!='naive']
    naive=[r for r in authors if r['loss_mode']=='naive']
    assert len(aa)==96 and len(naive)==48
    assert all(r['field_changes_player1_terminal'] and r['post_step_exploitable'] for r in aa)
    naive_max=max(abs(x) for r in naive for row in r['gradient'] for x in row)
    assert naive_max<1e-6
    central=next(r for r in primary['central_cases'] if r['coupling']==.1)
    selected=[r for r in authors if r['coupling']==.1 and not r['proximal'] and not r['normalize_advantages']
              and r['lmbda']==0 and r['dtype']=='float64']
    table=[dict(operator='paper_Eq8_joint',field=central['field'][0][1],BRgap2=central['after_step']['gains'][1])]
    table += [dict(operator=r['loss_mode'],field=r['gradient'][0][1],BRgap2=r['after_step']['gains'][1]) for r in selected]
    with (B/'results/V205_CENTRAL_OPERATOR_COMPARISON.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['operator','field','BRgap2']);writer.writeheader();writer.writerows(table)
    synthesis=dict(study='V205',status='INTERNALLY_CONFIRMED_MATHEMATICAL_COUNTEREXAMPLE',
        primary_H1=primary['H1'],registration_commit=reg['registration_commit'],
        source_freeze_unchanged=True,primary_outputs_unchanged=True,
        literal_profiles=320,source_helper_calls=144,AA_source_calls=96,naive_source_calls=48,
        independent_stochastic_replications=0,exact_game_paths=16,deterministic_BR_policies_per_player=8,
        central=dict(gamma=.9,beta=.3,alpha=.1,coupling=.1,terminal_field=central['field'][0][1],
            exact_player2_regret=central['after_step']['gains'][1]),
        maximum_beta0_or_marginal_control_field=zero_error,maximum_naive_source_control_field=naive_max,
        AA_source_minimum_regret=min(r['after_step']['gains'][1] for r in aa),
        AA_source_maximum_regret=max(r['after_step']['gains'][1] for r in aa),
        independent_internal_JS_completed=True,JS=js,symbolic=symbolic,
        post_hoc_intervention_summary={k:v for k,v in intervention.items() if k!='rows'},
        cancellation_scope='Independent current action sampling, detached current opponent marginal, and pre-current-action measurable past weights; not arbitrary past sampled GAE',
        published_publisher_copy_checked=True,
        theorem_scope='Joint-action Equation 8/10 and sampled original loss helpers, not a distinct unconditional-inner-expectation interpretation of Eq66',
        implementation_scope='Unmodified extracted original loss helper bodies on own tabular game; no original network/environment/training reproduction',
        scientific_external_confirmation=False,original_priority_established=False,
        new_N1_awards=[],N2=0,N3=0,historical_CT2=61,new_branch_score=None,overall_goal='ACTIVE',
        runtime=dict(python=platform.python_version(),numpy=np.__version__,
            node=subprocess.check_output(['node','--version']).decode().strip()))
    target.write_text(json.dumps(synthesis,indent=2),encoding='utf-8')
    fig,axes=plt.subplots(1,2,figsize=(11,3.6),layout='constrained')
    labels=['Eq8','PG simple','Fuente: integrada','Fuente: separada']
    axes[0].bar(labels,[r['field'] for r in table],color=['#146b8c','#8b8e95','#e18a32','#7b62a3'])
    axes[0].set_ylabel('Campo en un logit terminal del jugador 1')
    axes[0].set_title('Mismo equilibrio; escalas de pérdida diferentes',fontsize=10)
    axes[0].tick_params(axis='x',labelsize=8);axes[0].grid(axis='y',alpha=.2)
    alpha=np.linspace(0,1,250)
    for c,color in [(0.,'#146b8c'),(.1,'#e18a32')]:
        y=.9*(1+c)*np.tanh(alpha*.3*.9**3/8)
        axes[1].plot(alpha,y,label=f'c={c:g}',color=color)
        axes[1].plot([.1],[.9*(1+c)*np.tanh(.1*.3*.9**3/8)],'o',color=color)
    axes[1].set_xlabel('Tamaño del paso α (Eq8)');axes[1].set_ylabel('Ganancia de mejor respuesta del jugador 2')
    axes[1].set_title('Curva analítica; punto registrado α=0,1',fontsize=10)
    axes[1].legend();axes[1].grid(alpha=.2)
    fig.suptitle('V205: la alineación conjunta puede abandonar un equilibrio Nash',fontsize=12)
    fig.savefig(B/'results/FIG_V205_NASH_DEPARTURE.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
    for ax,limits in zip(axes,[(0,100),(55,65)]):
        ax.set_ylim(*limits);ax.set_xlim(-.4,2.4);ax.plot([0],[61],'o',color='#374a62')
        ax.axvspan(.6,2.4,color='#ddd',alpha=.5)
        ax.text(1.5,limits[0]+.45*(limits[1]-limits[0]),'Rama D2 sin puntuar\nPrioridad y confirmación externa pendientes',ha='center',fontsize=8)
        ax.set_xticks([0,1.5],['61 histórico','V205']);ax.set_ylabel('CT2');ax.grid(axis='y',alpha=.2)
    axes[0].set_title('Escala completa');axes[1].set_title('Vista ampliada del histórico')
    fig.suptitle('Un contraejemplo interno no concede automáticamente 2/3',fontsize=11)
    fig.savefig(B/'results/FIG_V205_CT2_UNCHANGED.png',dpi=160);plt.close(fig)
    print(json.dumps({k:v for k,v in synthesis.items() if k not in ['JS','symbolic','post_hoc_intervention_summary']},indent=2))


if __name__=='__main__':main()
