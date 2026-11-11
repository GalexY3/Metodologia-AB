"""Derived tables, paired-case bootstrap and provenance for V18."""
from pathlib import Path
from collections import defaultdict
import json,csv
import numpy as np
ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results'
def load(path):
    if not path.exists():return []
    return json.loads(path.read_text(encoding='utf8'))['rows']
def get_all():
    rows=load(RESULTS/'frozen_initial.json')+load(RESULTS/'frozen_sweep.json')+load(RESULTS/'frozen_onpolicy.json')
    unique={}
    for r in rows:
        key=(r['model'],r['case'],r['mode'])
        if key in unique:
            assert abs(r['food']-unique[key]['food'])<1e-5,key
        else:unique[key]=r
    return list(unique.values())
def aggregate(rows):
    table=[]
    for name in sorted({x['model'] for x in rows}):
        for mode in ('normal','scrambled_senders','no_messages'):
            z=[x for x in rows if x['model']==name and x['mode']==mode]
            if not z:continue
            worlds=sum(x['worlds'] for x in z)
            exact=sum(x['exact'] for x in z)
            table.append(dict(model=name,mode=mode,cases=len(z),worlds=worlds,
             food=sum(x['food']*x['worlds'] for x in z)/worlds,
             exact=exact,ever=sum(x['ever_exact'] for x in z),
             exact_rate=exact/worlds,
             occupied=float(np.mean([x['occupied'] for x in z]))))
    return table
def compare(rows,a,b,B=5000):
    ra={x['case']:x for x in rows if x['model']==a and x['mode']=='normal'}
    rb={x['case']:x for x in rows if x['model']==b and x['mode']=='normal'}
    cases=sorted(set(ra)&set(rb))
    if len(cases)<4:return None
    df=np.asarray([ra[k]['food']-rb[k]['food'] for k in cases])
    dx=np.asarray([ra[k]['exact']/ra[k]['worlds']-rb[k]['exact']/rb[k]['worlds'] for k in cases])
    rng=np.random.default_rng(20261111)
    idx=rng.integers(0,len(cases),(B,len(cases)))
    f_ci=np.quantile(df[idx].mean(axis=1),[.025,.975]).tolist()
    x_ci=np.quantile(dx[idx].mean(axis=1),[.025,.975]).tolist()
    return dict(first=a,second=b,n_cases=len(cases),
      delta_food=float(df.mean()),food_ci=f_ci,
      delta_exact=float(dx.mean()),exact_ci=x_ci,
      cases_positive=int((df>0).sum()))
def main():
    rows=get_all()
    if not rows:
        print('NO_FROZEN_RESULTS',flush=True);return
    table=aggregate(rows)
    pairs=[]
    for suffix,teacher in (('6111','teacher_v17_DISTILL_LATTICE_R8_s3111_fix'),
                           ('7111','teacher_v17_DISTILL_LATTICE_R8_s4111_fix')):
        baseline='v18_BC0_s'+suffix
        for prefix in ('v18_BC08_s','v18_BC3_s','v18_ON_SINGLE_3_s','v18_ON_ALL_3_s'):
            candidate=prefix+suffix
            for other in (baseline,teacher):
                result=compare(rows,candidate,other)
                if result:pairs.append(result)
    (RESULTS/'v18_statistics.json').write_text(json.dumps(
      dict(n_cells=len(rows),model_count=len(set(x['model'] for x in rows)),
           table=table,paired_case_bootstrap=pairs),indent=2),encoding='utf8')
    lines=['# V18 — Estabilidad de la organización durante aprendizaje individual','',
     'Informe derivado de evaluaciones congeladas; ninguna página web generada.',
     '',
     'El aprendizaje de refuerzo utiliza exclusivamente la ración individual como recompensa. El término de regularización utiliza una política de coordinación aprendida por imitación de un profesor programado y debe distinguirse de cooperación descubierta autónomamente.',
     '',
     '## Métricas fuera de muestra','',
     '| Política | Comunicación | Casos | Sociedades | Comida | Exactos | Porcentaje exacto |',
     '|---|---|---:|---:|---:|---:|---:|']
    for r in table:
        lines.append(f'| {r["model"]} | {r["mode"]} | {r["cases"]} | {r["worlds"]} | {r["food"]:.4f} | {r["exact"]} | {r["exact_rate"]:.2%} |')
    lines+=['','## Contrastes pareados (primer modelo menos segundo)','',
     'Intervalos por bootstrap de 5.000 remuestreos de escenarios completos. Son descriptivos y no cubren la incertidumbre entre muchas nuevas inicializaciones de redes.',
     '',
     '| Contraste | Diferencia de comida | IC 95 % por escenario | Diferencia en reparto exacto | IC 95 % | Casos favorables |',
     '|---|---:|---|---:|---|---:|']
    for x in pairs:
        f0,f1=x['food_ci'];e0,e1=x['exact_ci']
        lines.append(f'| {x["first"]} − {x["second"]} | {x["delta_food"]:+.4f} | [{f0:+.4f}, {f1:+.4f}] | {100*x["delta_exact"]:+.2f} pp | [{100*e0:+.2f}, {100*e1:+.2f}] pp | {x["cases_positive"]}/{x["n_cases"]} |')
    lines+=['','## Alcance inferencial','',
     'El conjunto de tareas incluye M/k conocidos y nuevas combinaciones de M/k. Las semillas de mundos son nuevas y se emparejan entre tratamientos. Algunas políticas se seleccionaron durante pilotos anteriores, por lo que este estudio conserva carácter confirmatorio limitado.',
     '',
     'El número de trabajadores que obtiene comida y el número de profesiones son distintos resultados; para afirmar organización correcta se exige exactamente k grupos equilibrados.',
     'La intervención que elimina mensajes modifica la disponibilidad del protocolo programado y no demuestra por sí sola cooperación social aprendida.',
     'Se registran tanto repartos exactos al final como alcanzados en algún momento del episodio, para estudiar fragilidad y estabilidad.',
     '',
     'Las rutas fuente y el código de entrenamiento se encuentran en los directorios v17_regime_coalition y v18_retention del mismo repositorio.']
    (ROOT/'RESULTADOS_V18.md').write_text('\n'.join(lines),encoding='utf8')
    cols=('model','case','m','k','initialization','mode','food','D','occupied','exact','ever_exact','worlds','exact_frames')
    with (ROOT/'COMPARACION_V18.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for row in rows:writer.writerow({name:row.get(name) for name in cols})
    print('ANALYSIS_COMPLETE',len(rows),'conditions',
      len(table),'model-modes',len(pairs),'paired_contrasts',flush=True)
    for r in table:
        if r['mode']=='normal':
            print('CHECKPOINT',r['model'],'FOOD',round(r['food'],4),'EXACT',r['exact'],'/',r['worlds'])
if __name__=='__main__':main()
