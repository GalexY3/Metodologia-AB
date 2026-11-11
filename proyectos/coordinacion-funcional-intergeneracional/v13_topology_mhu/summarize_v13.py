"""Summarize original V13 frozen-world evaluations, keeping seed and N distinct."""
from __future__ import annotations
from pathlib import Path
import csv,json,collections
import numpy as np
import networkx as nx
from network_v13 import HERE,build_graph,coordinates
from mhu_v13 import low_phases

ROWS=[]
for f in sorted((HERE/'evaluations').glob('v13_N*_EVAL.json')):
    data=json.loads(f.read_text('utf8'))
    net=data['network']
    for e in data['experiments']:
        if e['graph_seed']!=net['graph_seed']:continue
        if e['init']!='random' or e['baseline']!='learned':continue
        if e['task'] not in ('known_k2_m10','known_k4_m20','unseen_k5_m30'):continue
        last=[z['checks'][str(z['replay'][-1]['t'] if z['replay'] else 60)] for z in e['by_seed']]
        windows=[x['finite_window_ratio'] for x in last if x['finite_window_ratio'] is not None]
        coverage=[x['alive_spectrum']['mean_resolved_components'] for x in last]
        ROWS.append(dict(name=data['name'],n=net['n'],topology=net['network'],
          degree=net['mean_degree'],links=net['links'],degree_sd=net['degree_std'],
          graph_path=net['path_length'],clustering=net['clustering'],
          graph_seed=net['graph_seed'],task=e['task'],
          food=e['food'],dist=e['d'],exact=e['exact'],worlds=e['n_worlds'],
          low_ratio=e['low_spectral_ratio'],
          window_ratio=float(np.mean(windows)) if windows else None,
          covered_components=float(np.mean(coverage))))
out=HERE/'AGREGADO_V13.csv'
with out.open('w',encoding='utf-8',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(ROWS[0]))
    w.writeheader();w.writerows(ROWS)
lines=['# V13 — Resultados automáticamente consolidados',
'',
'Batería **exploratoria**; todas las cifras son de pesos congelados, dos semillas de mundo por fila (32 sociedades cada una), 60 turnos. No atribuir significación estadística a una sola semilla de entrenamiento.',
'',
'| Población | Topología | Grado medio | Comida k=4 | Exactos k4 | Comida M30/k5 | Ratio espectral M30/k5 | Ratio ventanas M30/k5 |',
'|---:|---|---:|---:|---:|---:|---:|---:|']
group={}
for row in ROWS:group.setdefault(row['name'],{})[row['task']]=row
for name,bytask in sorted(group.items()):
    try:
        a=bytask['known_k4_m20'];b=bytask['unseen_k5_m30']
    except KeyError:continue
    def fmt(x):return 'indefinido' if x is None else f'{x:.3f}'
    lines.append(f"| {a['n']} | {a['topology']} (s{name.split('_s')[-1]}) | {a['degree']:.1f} | {a['food']:.3f} | {a['exact']}/{a['worlds']} | {b['food']:.3f} | {fmt(b['low_ratio'])} | {fmt(b['window_ratio'])} |")
lines.extend(['','## Comprobación del soporte espacial frente a las profesiones','',
'El factor de estructura total de las POSICIONES se calcula como media de |sum exp(-2πiqx)|²/N, en las seis frecuencias bajas. No equivale al factor de estructura de las profesiones ni define la MHU de marcas.','',
'| N | Soporte | Factor espacial total de baja frecuencia |',
'|---:|---|---:|'])
for n in [60,120]:
    for t in ['torus','jitter_geo','poisson_geo']:
        xy=coordinates(n,t,4000)
        s=float((abs(low_phases(xy).sum(0))**2).mean()/n)
        lines.append(f'| {n} | {t} | {s:.5f} |')
for n in [60,120]:
    pad=build_graph(n,8,'modular',4000)
    g=nx.Graph()
    g.add_nodes_from(range(n))
    for i,neighbors in enumerate(pad):
        g.add_edges_from((i,int(j)) for j in neighbors if j>=0)
    groups=[set(range(i*n//4,(i+1)*n//4)) for i in range(4)]
    lines.append(f'\nModularidad con comunidades PLANTADAS (N={n}, d8, semilla4000): {nx.community.modularity(g,groups):.4f}. La modularidad espacial por cuadrantes de NETWORK.json es otra partición y no debe confundirse.')
lines.extend(['','## Advertencia metodológica','',
'Un ratio espectral o de ventanas inferior a 1 es supresión de fluctuaciones en una muestra FINITA; no establece S(q)→0 para q→0. Cuando los agentes colapsan en 1–2 profesiones, los componentes pueden no cumplir la cantidad mínima de 4 trabajadores; el ratio puede ser indefinido. Nunca codificarlo como cero.',
'El modelo no recibe recompensas por MHU ni se entrena para maximizar directamente estos indicadores. La intervención de etiquetas optimizadas es exclusivamente un control positivo artificial.'])
(HERE/'RESULTADOS_V13_AUTO.md').write_text('\n'.join(lines),encoding='utf8')
print('AUTO_SUMMARY',len(ROWS),'evaluated conditions',len(group),'agents')
print('REPORT_PATH',HERE/'RESULTADOS_V13_AUTO.md')
