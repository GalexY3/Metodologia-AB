"""V17-DualRL: privately trained two-sided neural coordination (no shared weights).

Agent independently learns THREE Bernoulli decisions: pledge for a new career
when congested, join a neighbor's career when deficit, and advertise its own
underfilled career. Invitations pass through local rounds before any physical
change; quorum for genuinely new career proposals. The action heads are
learned using realized individual food only. Permutation-equivariant role
operations are hand-designed scaffolds, not trained end to end.
"""
from __future__ import annotations
import os,math,torch
from torch import nn
from torch.distributions import Bernoulli
import neural_pledge as p

class DualNet(nn.Module):
 def __init__(self,n,h=16,rounds=8,quorum=True,features='lattice',
              scramble=False,gate=True):
  super().__init__()
  self.n=n;self.h=h;self.rounds=rounds;self.quorum=quorum
  self.features=features;self.scramble=scramble;self.gate=gate
  self.wx=nn.Parameter(torch.randn(n,14,h)*(.6/math.sqrt(14)))
  self.b=nn.Parameter(torch.zeros(n,h))
  self.v=nn.Parameter(torch.randn(n,h,3)*(.3/math.sqrt(h)))
  self.bias=nn.Parameter(torch.zeros(n,3))
  self._cached_reach=None
  with torch.no_grad():
   self.bias[:,0]=0. # congested founding
   self.bias[:,1]=.4 # deficit consolidation
   self.bias[:,2]=0. # deficit advertise
  self.reset()
 def reset(self):
  self.emafood=None;self.emaown=None;self.prevjob=None
 def act(self,e,greedy=False,disable_messages=False,alter_messages=False):
  c=e.c;b,n=e.jobs.shape;q=n/c.k
  loc=e.local()
  own=loc.gather(2,e.jobs[...,None]).squeeze(2)
  if self.emafood is None or self.emafood.shape!=e.food.shape:
   self.emafood=e.food.detach()
   self.emaown=own.detach()
   self.prevjob=e.jobs.detach().clone()
  self.emafood=(.8*self.emafood+.2*e.food).detach()
  self.emaown=(.75*self.emaown+.25*own).detach()
  r=e.food
  sub=q*r;sup=q/r.clamp_min(1e-6)
  okunder=(sub>=1-1e-5)&(sub<q-1e-5)&((sub-sub.round()).abs()<2e-4)
  okover=(sup>q+1e-5)&(sup<=n+1e-5)&((sup-sup.round()).abs()<2e-4)
  local_sign=torch.where(own>(q-1)/(n-1),torch.ones_like(r),
                         -torch.ones_like(r))
  sign=torch.where(okunder&~okover,-torch.ones_like(r),
       torch.where(okover&~okunder,torch.ones_like(r),
         torch.where(r>=1-1e-5,torch.zeros_like(r),local_sign)))
  if self.features=='raw':
   signfeat=torch.zeros_like(sign)
   quantfeat=torch.zeros_like(r)
  elif self.features=='local':
   signfeat=local_sign
   quantfeat=torch.zeros_like(r)
  elif self.features=='oracle':
   # This treatment is INCORRECT as a decentralized policy. Diagnostic only!
   sign=torch.sign(e.counts.gather(1,e.jobs)-q)
   signfeat=sign
   quantfeat=torch.ones_like(r)
  else:
   signfeat=sign
   quantfeat=((sub-sub.round()).abs()-(sup-sup.round()).abs()).clamp(-1,1)
  def const(v):return torch.full_like(r,float(v))
  obs=torch.stack([r,1-r,own,self.emaown,self.emafood,
   const(c.k/c.m),const(q/n),const(math.log(q)/math.log(n)),
   signfeat,quantfeat,(self.prevjob!=e.jobs).float(),
   const(e.t/c.horizon),const(c.degree/n),
   const(math.log(c.m)/math.log(80))],dim=-1)
  hidden=torch.tanh(torch.einsum('bnd,ndh->bnh',obs,self.wx)+self.b[None,:,:])
  logits=torch.einsum('bnh,nhv->bnv',hidden,self.v)+self.bias[None,:,:]
  dist=Bernoulli(logits=logits)
  samples=(logits>0).float() if greedy else dist.sample()
  if self.gate:
   under=sign<0
   over=sign>0
  else:
   under=r<.9999
   over=r<.9999
  valid=torch.stack([over,under,under&(r<.9999)],dim=2)
  lp=(dist.log_prob(samples)*valid.float()).sum(2)
  entropy=(dist.entropy()*valid.float()).sum(2)
  pledge=samples[:,:,0].bool()&over
  join=samples[:,:,1].bool()&under
  invite=samples[:,:,2].bool()&under
  # Local modal career (argmax of neighbor occupations), permutation
  # equivariant in distribution since ties are broken by independent noise.
  scores=loc+torch.rand_like(loc)*1e-5
  modal=scores.argmax(2)
  join &=modal!=e.jobs
  # Candidate new profession drawn from locally vacant labels.
  proposed=torch.randint(c.m,(b,n),device=c.device)
  for _ in range(5):
   taken=(loc.gather(2,proposed[:,:,None]).squeeze(2)>0)|(proposed==e.jobs)
   proposed=torch.where(taken,torch.randint(c.m,(b,n),device=c.device),proposed)
  dest=proposed.clone()
  is_recruit=torch.zeros((b,n),dtype=torch.bool,device=c.device)
  if self.rounds>0 and not disable_messages:
   # Invitations win destination priority, then normal founding proposals.
   first=torch.rand((b,n),device=c.device)*.05
   second=1+torch.rand((b,n),device=c.device)
   key=torch.where(invite,first,
       torch.where(pledge,second,torch.full_like(first,float('inf'))))
   dest=torch.where(invite,e.jobs,proposed)
   is_recruit=invite.clone()
   for _ in range(self.rounds):
    keys=key[:,e.adj];offers=dest[:,e.adj];types=is_recruit[:,e.adj]
    if alter_messages:
     ix=torch.randint(n,(b,n,c.degree),device=c.device)
     keys=key.gather(1,ix.reshape(b,-1)).reshape(b,n,c.degree)
     offers=dest.gather(1,ix.reshape(b,-1)).reshape(b,n,c.degree)
     types=is_recruit.gather(1,ix.reshape(b,-1)).reshape(b,n,c.degree)
    table=torch.cat([key[...,None],keys],dim=2)
    pick=table.argmin(2,keepdim=True)
    dest=torch.cat([dest[...,None],offers],dim=2).gather(2,pick).squeeze(2)
    is_recruit=torch.cat([is_recruit[...,None],types],dim=2).gather(2,pick).squeeze(2)
    key=table.gather(2,pick).squeeze(2)
   if self.scramble:
    # Independent receiver reassignment breaks any common destination
    # even though the proposal vocabulary remains the same.
    ix=torch.randint(n,(b,n),device=c.device)
    dest=dest.gather(1,ix)
    is_recruit=is_recruit.gather(1,ix)
   if self.quorum:
    if self._cached_reach is not None and c.topology=='ring':
     reach=self._cached_reach
    else:
     reach=torch.eye(n,device=c.device,dtype=torch.bool)
     for _ in range(self.rounds):
      reach=reach|reach[e.adj].any(1)
     if c.topology=='ring':self._cached_reach=reach
    matching=dest[:,:,None]==dest[:,None,:]
    visible_pledges=(reach[None,:,:]&matching&pledge[:,None,:]).sum(2)
    # A worker joining an already underfull career does not require
    # a founder quorum. In a new empty career, require > q*r pledges.
    acceptable=is_recruit|(visible_pledges>q*r)
    pledge &=acceptable
  elif self.quorum:
   pledge &=1>q*r
  # Simultaneous physical job changes after complete signaling.
  jobs=torch.where(join,modal,e.jobs)
  jobs=torch.where(pledge,dest,jobs)
  self.prevjob=e.jobs.detach().clone()
  return jobs,lp,entropy

if __name__=='__main__':
 args=p.parse()
 p.PledgeActor=DualNet
 p.main(args)
