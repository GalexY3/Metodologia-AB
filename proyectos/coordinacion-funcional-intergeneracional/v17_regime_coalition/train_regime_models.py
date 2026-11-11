"""Neural inference of surplus/deficit from truly local features and food.

12 competing classifier models: two seeds each x six architectures/feature
conditions. This is an auxiliary diagnosis, NOT a trained coordination policy.
A separate OOD benchmark with unseen k/degree/topology tests generalization.
"""
from __future__ import annotations
import os,sys,time,itertools,math,random,json
from pathlib import Path
from dataclasses import dataclass,replace
import torch,numpy as np
from torch import nn
from torch.nn import functional as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12
N=120
torch.set_num_threads(3)

def make_dataset(name,config_set,seed=11001,batch=12):
 rng=np.random.default_rng(seed)
 Xs=[];Ys=[];Meta=[]
 for idx,(m,k,d,topo,init) in enumerate(config_set):
  cfg=v12.Config(n=N,m=m,k=k,degree=d,topology=topo,batch=batch,device='cpu')
  w=v12.World(replace(cfg,init='trap' if init=='trap' else 'random'),seed+idx*37)
  if init=='cluster':
   for b in range(batch):
    groups=min(m,max(2,k//2))
    roles=torch.from_numpy(rng.choice(m,groups,replace=False)).long()
    membership=roles[torch.arange(N)*groups//N]
    w.jobs[b,:]=membership
   w.food,w.counts=v12.food(w.jobs,cfg.m,cfg.k)
  f=w.local().gather(2,w.jobs[...,None]).squeeze(2).numpy()
  own=w.jobs.numpy()
  counts=w.counts.gather(1,w.jobs).numpy()
  r=w.food.numpy()
  q=N/k
  # Everything here except y is admissible locally.
  local=f
  # Explore exact integer lattice, which can be inferred from personal
  # reward only. Never feed true counts to network.
  sub=q*r;sup=q/np.maximum(r,1e-8)
  subres=np.abs(sub-np.rint(sub))
  supres=np.abs(sup-np.rint(sup))
  basic=np.stack([
   r,1-r,np.full_like(r,q/N),np.full_like(r,k/N),
   np.full_like(r,m/N),local,k*local,
   local-(q-1)/(N-1),np.full_like(r,d/N),
   np.full_like(r,math.log(q)/math.log(N))],axis=-1)
  extra=np.stack([
   subres,supres,(subres<1e-5).astype('float32'),
   (supres<1e-5).astype('float32'),
   np.clip(sub/N,0,1),np.clip(sup/N,0,1),
   ((sub<q)&(sup>q)).astype('float32'),
   np.abs(np.log(np.maximum(r,1e-8))),
   np.full_like(r,float(init=='cluster'))
   ],axis=-1)
  # Important: The last "init==cluster" feature must NOT be used:
  # it reveals how the researcher initialized the world. Drop it.
  extra=extra[...,:-1]
  x=np.concatenate([basic,extra],axis=-1).reshape(-1,basic.shape[-1]+extra.shape[-1]).astype('float32')
  y=np.sign(counts-q).astype(int).reshape(-1)+1
  Xs.append(x);Ys.append(y.astype('int64'))
  Meta.extend([dict(m=m,k=k,degree=d,topology=topo,init=init)]*(len(y)))
 X=np.concatenate(Xs);Y=np.concatenate(Ys)
 print('DATASET',name,'conditions',len(config_set),'samples',len(Y),
       'labels',np.bincount(Y,minlength=3),flush=True)
 return X,Y,Meta

def analyze(y,pred,meta):
 confusion=np.zeros((3,3),dtype=np.int64)
 np.add.at(confusion,(y,pred),1)
 perclass=np.diag(confusion)/np.maximum(1,confusion.sum(axis=1))
 out=dict(accuracy=float(np.mean(y==pred)),
    balanced_accuracy=float(np.mean(perclass)),
    macro_precision=float(np.mean(np.diag(confusion)/np.maximum(1,confusion.sum(axis=0)))),
    matrix=confusion.tolist(),recall_per_class=perclass.tolist(),
    n=len(y),cases={})
 for init in ('random','trap','cluster'):
  mask=np.array([z['init']==init for z in meta])
  if mask.any():
   yc=y[mask];pr=pred[mask]
   mat=np.zeros((3,3),dtype=np.int64)
   np.add.at(mat,(yc,pr),1)
   per=np.diag(mat)/np.maximum(1,mat.sum(1))
   out['cases'][init]=dict(accuracy=float((yc==pr).mean()),
      balanced_accuracy=float(np.mean(per)),n=int(mask.sum()))
 return out

class Predictor(nn.Module):
 def __init__(self,nfeat,h,depth):
  super().__init__()
  if depth==0:self.net=nn.Linear(nfeat,3)
  elif depth==1:self.net=nn.Sequential(nn.Linear(nfeat,h),nn.Tanh(),nn.Linear(h,3))
  else:self.net=nn.Sequential(nn.Linear(nfeat,h),nn.Tanh(),
    nn.Linear(h,h),nn.Tanh(),nn.Linear(h,3))
 def forward(self,x):return self.net(x)

def train(variant,seed,X,Y,V,T,device='cuda',steps=850):
 torch.manual_seed(seed)
 np.random.seed(seed)
 use_lattice='lattice' in variant
 nfeat=18 if use_lattice else 10
 Xtr=torch.as_tensor(X[:,:nfeat],device=device)
 Ytr=torch.as_tensor(Y,device=device)
 Xv=torch.as_tensor(V[:,:nfeat],device=device)
 if 'linear' in variant:depth=0;hidden=0
 elif 'deep' in variant:depth=2;hidden=48
 elif 'wide' in variant:depth=1;hidden=64
 else:depth=1;hidden=24
 model=Predictor(nfeat,hidden,depth).to(device)
 opt=torch.optim.Adam(model.parameters(),lr=.002)
 weights=None
 if 'weighted' in variant:
  counts=np.bincount(Y,minlength=3)
  weights=torch.as_tensor(1/np.maximum(counts,1),dtype=torch.float32,device=device)
  weights=weights/weights.mean()
 for i in range(steps):
  idx=torch.randint(len(Ytr),(2048,),device=device)
  logits=model(Xtr[idx])
  loss=F.cross_entropy(logits,Ytr[idx],weight=weights)
  opt.zero_grad();loss.backward();opt.step()
  if i%250==0:
   with torch.no_grad():
    acc=float((model(Xv[:8192]).argmax(1)==torch.as_tensor(T[:8192],device=device)).float().mean())
   print('TRAIN',variant,seed,'step',i,'loss',round(float(loss),4),
         'eval_sample_acc',round(acc,4),flush=True)
 with torch.no_grad():
  pred=model(Xv).argmax(1).cpu().numpy()
 return model,pred

def main():
 import argparse
 ap=argparse.ArgumentParser()
 ap.add_argument('--seeds',default='3111,4111')
 ap.add_argument('--steps',type=int,default=850)
 ap.add_argument('--device',default='cuda')
 args=ap.parse_args()
 tr_k=(2,3,4,6,10,15,30,60)
 hold_k=(5,8,12,20,40)
 tr=[(m,k,d,'ring',init) for m,k,d,init in itertools.product(
     (12,24,40,80),tr_k,(4,8),('random','trap','cluster')) if m>=k]
 test=[(m,k,d,'rewired',init) for m,k,d,init in itertools.product(
     (24,40,80),hold_k,(8,16),('random','trap','cluster')) if m>=k]
 X,Y,_=make_dataset('train',tr,seed=811199,batch=16)
 V,T,meta=make_dataset('heldout',test,seed=913133,batch=20)
 baseline_v=np.sign(V[:,7]).astype('int64')+1
 baseline_y=analyze(T,baseline_v,meta)
 variants=['raw_mlp','raw_wide','raw_deep','lattice_mlp',
           'lattice_deep','lattice_weighted','lattice_linear']
 print('BASELINE_LOCAL',baseline_y['accuracy'],baseline_y['balanced_accuracy'],flush=True)
 outputs=[]
 for name in variants:
  for seed in [int(x) for x in args.seeds.split(',')]:
   model,pred=train(name,seed,X,Y,V,T,device=args.device,steps=args.steps)
   metrics=analyze(T,pred,meta)
   output=dict(name=name,seed=seed,features=18 if 'lattice' in name else 10,
      total_params=sum(p.numel() for p in model.parameters()),eval=metrics)
   outputs.append(output)
   torch.save(dict(model=model.state_dict(),name=name,seed=seed),
              HERE/'results'/f'regime_model_{name}_{seed}.pt')
   print('MODEL_SCORE',name,seed,'accuracy',
       round(metrics['accuracy'],4),'balanced',
       round(metrics['balanced_accuracy'],4),'cluster',
       round(metrics['cases']['cluster']['accuracy'],4),flush=True)
 summary=dict(train_ks=tr_k,holdout_ks=hold_k,
   heldout_topology='rewired',heldout_degree=[8,16],
   train_samples=len(Y),test_samples=len(T),local_baseline=baseline_y,
   variants=outputs,
   caveat='Auxiliary centralized classifier only; not proof of multiagent coordination.')
 dest=HERE/'results'/'regime_neural_v17.json'
 dest.write_text(json.dumps(summary,indent=2),encoding='utf8')
 print('NEURAL_REGIME_DONE',len(outputs),'models',
       'best',max(outputs,key=lambda x:x['eval']['balanced_accuracy'])['name'],flush=True)
if __name__=='__main__':main()
