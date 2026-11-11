"""Warm-history dose response, frozen trained neural policy (no re-training)."""
import json,torch,numpy as np
from pathlib import Path
from targeted_gifts import C,PrivateGiftActor,simulate
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(3)
rows=[]
for name in ('v19_TARGET_SOC_C12_s3111','v19_TARGET_SOC_C12_s4111'):
 p=ROOT/'runs'/name/'targeted_latest.pt'
 if not p.exists():continue
 spec=json.loads((ROOT/'runs'/name/'targeted_spec.json').read_text('utf8'))
 ck=torch.load(p,map_location='cpu',weights_only=False)
 actor=PrivateGiftActor(spec['n'],spec['hidden'],spec['init_scale']).to('cpu')
 actor.load_state_dict(ck['model'])
 actor.eval()
 for k,degree,topo in ((2,2,'ring'),(2,2,'rewired'),(2,4,'ring')):
  for warm in (0.,.25,.5,.75,1.):
   for mode in ('normal','no_social','scramble'):
    z=[]
    for j in range(8):
     c=C(n=spec['n'],k=k,degree=degree,topology=topo,
         batch=32,horizon=48,cost=spec['cost'],device='cpu',
         gamma=spec['gamma'],warm=warm)
     torch.manual_seed(193700+j*277+k*17+degree*3)
     result=simulate(c,actor,193700+j*277+k*17+degree*3,mode=mode,watch=True)[0]
     z.append(result)
    row=dict(name=name,update=ck['update'],k=k,degree=degree,
      topology=topo,warm=warm,mode=mode,worlds=sum(x['worlds'] for x in z),
      food=float(np.mean([x['food'] for x in z])),
      gift=float(np.mean([x['gift'] for x in z])),
      coverage=float(np.mean([x['coverage'] for x in z])))
    rows.append(row)
    if k==2 and degree==2 and topo=='ring':
     print('WARM_FROZEN',name,ck['update'],'warm',warm,'mode',mode,
       'food',round(row['food'],4),'gift',round(row['gift'],4),flush=True)
out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
(out/'warm_frozen_v19.json').write_text(json.dumps(dict(rows=rows),indent=1),encoding='utf8')
print('WARM_FROZEN_DONE',len(rows),'conditions',sum(x['worlds'] for x in rows),'worlds',flush=True)
