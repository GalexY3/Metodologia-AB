"""Exact known-method rival, not a new algorithm: LOLA-Ex equation (4.4).

Uses the V202 physical net returns with all received AND given transfers.
Oracle access to peer policies, losses and learning rule is explicit.
The derivative of grad_j(U_i) is stopped as in the original LOLA paper;
this is not the full derivative of a finite unrolled lookahead objective.
Inputs here are interior logit coordinates; projection belongs to a runner.
"""
import numpy as np
import torch
from torch.nn.functional import one_hot
from v202_relational_learning import AUT,F,Y,BETA


def values(theta,losses=(1.,1.,7.,7.),epsilon=0.):
    """Four normalized private discounted net returns from START."""
    assert theta.shape==(4,15,2,2)
    p=epsilon/2+(1-epsilon)*torch.sigmoid(theta)
    weights_g=theta.new_tensor([.2,.8]);weights_b=theta.new_tensor([.8,.2])
    modes=p[:,:,:,0]
    qg=(modes*weights_g).sum(2);qb=(modes*weights_b).sum(2)
    pay=(modes[:3]*p[:3,:,:,1]*weights_g).sum(2)/qg[:3]
    pg=.65*qg.prod(0);pb=.35*qb.prod(0)
    h=torch.arange(15,device=theta.device)
    ta=one_hot((h//3)*3,15).to(theta.dtype)
    tb=one_hot((h//3)*3+1,15).to(theta.dtype)
    transition=(1-pg-pb)[:,None]*ta+pb[:,None]*tb
    weights=[];destinations=[]
    for mask in range(8):
        weight=pg
        for j in range(3):weight=weight*(pay[j] if (mask>>j)&1 else 1-pay[j])
        weights.append(weight);destinations.append(mask.bit_count()*3+2)
    targets=one_hot(torch.tensor(destinations,device=theta.device),15).to(theta.dtype)
    transition=transition+torch.stack(weights,dim=1)@targets
    loss=theta.new_tensor(losses)[:,None]
    rewards=AUT+.8*F*pg[None,:]-(Y+loss)*pb[None,:]
    donor=rewards[:3]-.25*pg[None,:]*pay
    critical=rewards[3]+.25*pg*pay.sum(0)-.3*(.65*qg[3]+.35*qb[3])
    rewards=torch.cat([donor,critical[None,:]],dim=0).T
    system=torch.eye(15,dtype=theta.dtype,device=theta.device)-BETA*transition
    v=torch.linalg.solve(system,rewards)
    return (1-BETA)*v[12]


def all_gradients(theta,losses=(1.,1.,7.,7.),epsilon=0.,create_graph=True):
    u=values(theta,losses,epsilon)
    # G[i,j] is agent i's private return gradient in agent j's coordinates.
    g=torch.stack([torch.autograd.grad(u[i],theta,create_graph=create_graph,
        retain_graph=True)[0] for i in range(4)])
    return u,g


def lola_components(theta,losses=(1.,1.,7.,7.),epsilon=0.):
    """Own gradient and sum_j [grad_j U_i]^T Hessian_{i,j} U_j."""
    u,g=all_gradients(theta,losses,epsilon,create_graph=True)
    own=torch.stack([g[i,i] for i in range(4)])
    cross=[]
    for i in range(4):
        term=sum((g[j,j]*g[i,j].detach()).sum() for j in range(4) if j!=i)
        cross.append(torch.autograd.grad(term,theta,retain_graph=True)[0][i])
    return u,own,torch.stack(cross)


def field(flat,eta=1.,epsilon=0.,lola=True):
    theta=torch.tensor(np.asarray(flat).reshape((4,15,2,2)),dtype=torch.float64,requires_grad=True)
    if lola:
        _,own,correction=lola_components(theta,epsilon=epsilon)
        return (own+eta*correction).detach().numpy().ravel()
    _,g=all_gradients(theta,epsilon=epsilon,create_graph=False)
    return torch.stack([g[i,i] for i in range(4)]).detach().numpy().ravel()
