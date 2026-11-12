"""V34 frozen evaluator: same V30 causal tests but on degree-four topology."""
from __future__ import annotations
import argparse,json,torch
from pathlib import Path
from targeted_gifts import C as OriginalC
from v24_k4_joint import start4
import v30_frozen_audits as base
from v30_consensual import contract_step

ROOT=Path(__file__).resolve().parent
def degree4(*args,**kwargs):
 assert kwargs.get('degree')==6,kwargs
 kwargs['degree']=4
 return OriginalC(*args,**kwargs)

@torch.no_grad()
def oracle(c,seed=401):
 assert c.k==4 and c.degree==4 and c.topology=='ring'
 w=start4(c,seed,'balanced')
 n=c.n
 agents=torch.arange(n,device=c.device)
 third=torch.where((agents//2)%2==0,
    torch.full_like(agents,2),torch.full_like(agents,-2))
 offsets=torch.stack((torch.ones_like(agents),-torch.ones_like(agents),third),dim=1)
 recipients=((agents[:,None]+offsets)%n)[None,:,:].expand(c.batch,-1,-1)
 offers=torch.ones(c.batch,n,3,device=c.device)
 food,_=contract_step(c,w,recipients,offers)
 assert bool((w['full']==1).all())
 return dict(food=float(food.mean()),full=float(w['full'].mean()),
   cover=float(w['cover'].mean()),count=3.)

def main():
 parser=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
 parser.add_argument('--name',required=True)
 opts,_=parser.parse_known_args()
 spec=json.loads((ROOT/'runs'/opts.name/'v25_spec.json').read_text('utf8'))
 assert spec['v34_degree']==4 and spec['settlement']=='mutual'
 base.C=degree4
 base.oracle_contract=oracle
 print('V34_AUDIT_TOPOLOGY',opts.name,'degree4',flush=True)
 base.main()
if __name__=='__main__':main()
