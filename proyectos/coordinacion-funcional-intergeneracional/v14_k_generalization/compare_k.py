"""Compare same held-out scenarios using saved frozen evals; no selection."""
from pathlib import Path
import json,csv
HERE=Path(__file__).resolve().parent
filelist=sorted((HERE/'evaluations').glob('*_EVAL.json'))
datas={p.name.removesuffix('_EVAL.json'):json.loads(p.read_text('utf8')) for p in filelist}
def get(model,m,k,mode='learned'):
    d=datas.get(model)
    if not d:return None
    return next((x for x in d['evals'] if x['m']==m and x['k']==k and x['mode']==mode),None)
names=['v14_N120_knownK_s3111','v14_N120_hiddenK_s3111','v14_N120_curriculum_k2to15_s3111','v14_N120_fullrange_s3111']
rows=[]
for m in (12,40,80):
    for k in (2,3,4,5,6,8,10,12,15,20,24,30):
        for name in names:
            learned=get(name,m,k)
            if not learned:continue
            randomized=get(name,m,k,'random')
            imitate=get(name,m,k,'imitate')
            rows.append(dict(model=name,m=m,k=k,
                trained_k=k in datas[name]['training_k'],
                trained_m=m in datas[name]['training_M'],
                food=learned['avg_food'],
                dist=learned['avg_D'],
                exact=learned['exact'],
                n_worlds=learned['worlds'],
                viable=round(sum(x['viable'] for x in learned['by_seed'])/len(learned['by_seed']),5),
                occupied=learned['occupied'],
                baseline_random=randomized['avg_food'] if randomized else None,
                baseline_imitate=imitate['avg_food'] if imitate else None))
out=HERE/'COMPARACION_K.csv'
with out.open('w',encoding='utf8',newline='') as fh:
    writer=csv.DictWriter(fh,fieldnames=list(rows[0]))
    writer.writeheader();writer.writerows(rows)
models=' | '.join(names)
print('COMPARISON_MODELS',','.join(datas.keys()),flush=True)
print('m k   known_k   hidden_k  curriculum  random      imitat',flush=True)
for m in (40,80):
    for k in (2,3,4,5,6,8,10,12,15,20,24,30):
        x=[get(name,m,k) for name in names]
        if not any(x):continue
        rnd=next((get(name,m,k,'random') for name in names if get(name,m,k,'random')),None)
        imm=next((get(name,m,k,'imitate') for name in names if get(name,m,k,'imitate')),None)
        f=lambda x:format(x['avg_food'],'.4f') if x else '-'
        print(m,k,' ',*map(f,x),' ',f(rnd),' ',f(imm),flush=True)
print('CSV_READY',len(rows),flush=True)
