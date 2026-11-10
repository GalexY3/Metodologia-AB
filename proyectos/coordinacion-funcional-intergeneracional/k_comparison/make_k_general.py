"""One-time reproducible patch of a copied, frozen V9 village implementation.
Keeps the ten professions, individual training and per-agent weights unchanged.
"""
from pathlib import Path
p=Path(__file__).with_name("village.py")
s=p.read_text(encoding="utf-8")
edits=[
 ('def food_of_memberships(colors:torch.Tensor,n:int)', 'def food_of_memberships(colors:torch.Tensor,n:int,k:int=4)'),
 ('def measures(colors:torch.Tensor,food:torch.Tensor,counts:torch.Tensor,prev:Optional[torch.Tensor]=None)',
  'def measures(colors:torch.Tensor,food:torch.Tensor,counts:torch.Tensor,k:int=4,prev:Optional[torch.Tensor]=None)'),
 ('    n=colors.shape[1];q=n/4\n    top=torch.topk(counts,4,dim=1).values',
  '    n=colors.shape[1];q=n/k\n    top=torch.topk(counts,k,dim=1).values'),
 ('    q=n/4\n    foods=torch.minimum(per/q,q/per.clamp_min(1))',
  '    q=n/k\n    foods=torch.minimum(per/q,q/per.clamp_min(1))'),
 ('        "D4":float(d.mean())', '        "Dk":float(d.mean())'),
 ('class Config:\n    n:int=36', 'class Config:\n    n:int=36\n    k:int=4'),
 ('food_of_memberships(self.colors,cfg.n)', 'food_of_memberships(self.colors,cfg.n,cfg.k)'),
 ('food_of_memberships(new,self.cfg.n)', 'food_of_memberships(new,self.cfg.n,self.cfg.k)'),
 ('        v=measures(e.colors,e.food,e.counts)', '        v=measures(e.colors,e.food,e.counts,cfg.k)'),
 ('torch.topk(e.counts[0],4).values,torch.tensor(cfg.n/4,device=e.counts.device)',
  'torch.topk(e.counts[0],cfg.k).values,torch.tensor(cfg.n/cfg.k,device=e.counts.device)'),
 ('D4=float(1-torch.minimum(', 'Dk=float(1-torch.minimum('),
 ('train_D4=r["final"]["D4"]', 'train_Dk=r["final"]["Dk"]'),
 ('    if args.n%4 or args.n<12:raise ValueError("n must be divisible by 4 and >=12")',
  '    if args.k not in (2,4):raise ValueError("comparison only tests k=2 or k=4")\n    if args.n%args.k or args.n<12:raise ValueError("n must be divisible by k and >=12")'),
 ('cfg=Config(n=args.n,batch=args.batch,horizon=args.horizon,', 'cfg=Config(n=args.n,k=args.k,batch=args.batch,horizon=args.horizon,'),
 ('"version":"v9_village_pilot_1"', '"version":"k_comparison_1"'),
 ('"D4",round(ev["final"]["D4"],4)', '"Dk",round(ev["final"]["Dk"],4)'),
 ('    p.add_argument("--n",type=int,default=36)', '    p.add_argument("--n",type=int,default=36)\n    p.add_argument("--k",type=int,default=4)'),
]
for old,new in edits:
    n=s.count(old)
    if n!=1:raise RuntimeError(f"Expected exactly one {old[:55]!r}, found {n}")
    s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print(f"GENERALIZED k=2,k=4: {p}")
