"""Exact independent-player gradients in the V202 public repeated game.

Oracle control: knows physical probabilities AND all peer policies. Each
gradient optimizes that player's own return, but is not a private learner.
Public count/outcome histories reduce the 27-state bitmask chain to 15 states.
"""
import math
import numpy as np
from numba import njit
from v202_relational_learning import AUT,F,Y,BETA

START=12


@njit(cache=True)
def probability(theta):
    return 1/(1+np.exp(-np.minimum(12.,np.maximum(-12.,theta))))


@njit(cache=True)
def model(theta,losses,epsilon=0.):
    p=epsilon/2+(1-epsilon)*probability(theta)
    transition=np.zeros((15,15));reward=np.full((15,4),AUT)
    qg=np.zeros((15,4));qb=np.zeros((15,4));pay=np.zeros((15,3));good=np.zeros(15)
    for h in range(15):
        for i in range(4):
            qg[h,i]=.2*p[i,h,0,0]+.8*p[i,h,1,0]
            qb[h,i]=.8*p[i,h,0,0]+.2*p[i,h,1,0]
            if i<3:
                pay[h,i]=(.2*p[i,h,0,0]*p[i,h,0,1]+.8*p[i,h,1,0]*p[i,h,1,1])/qg[h,i]
        pg=.65*np.prod(qg[h]);pb=.35*np.prod(qb[h]);good[h]=pg
        transition[h,(h//3)*3]+=max(0.,1-pg-pb)
        transition[h,(h//3)*3+1]+=pb
        for mask in range(8):
            weight=pg;count=0
            for j in range(3):
                a=(mask>>j)&1;count+=a
                weight*=pay[h,j] if a else 1-pay[h,j]
            transition[h,count*3+2]+=weight
        for i in range(4):
            reward[h,i]+=.8*F*pg-(Y+losses[i])*pb
            if i<3:reward[h,i]-=.25*pg*pay[h,i]
        reward[h,3]+=.25*pg*pay[h].sum()-.3*(.65*qg[h,3]+.35*qb[h,3])
    system=np.eye(15)-BETA*transition
    values=np.linalg.solve(system,reward)
    start=np.zeros(15);start[START]=.05
    occupancy=np.linalg.solve(system.T.copy(),start)
    return p,transition,reward,values,occupancy,qg,qb,pay,good


@njit(cache=True)
def gradients(theta,losses,epsilon=0.):
    p,tr,r,v,d,qg,qb,pay,good=model(theta,losses,epsilon)
    base=probability(theta)
    gradient=np.zeros_like(theta);fisher=np.zeros_like(theta)
    advantages=np.zeros_like(theta)
    for h in range(15):
        ha=(h//3)*3;hb=ha+1
        for i in range(4):
            for s in range(2):
                posterior=52/59 if s else 13/41
                signal_prob=.59 if s else .41
                pg=posterior;pb=1-posterior
                for j in range(4):
                    if j!=i:pg*=qg[h,j];pb*=qb[h,j]
                if i<3:
                    future=np.zeros(2)
                    for ownpay in range(2):
                        for mask in range(8):
                            if ((mask>>i)&1)!=ownpay:continue
                            weight=1.;count=0
                            for j in range(3):
                                a=(mask>>j)&1;count+=a
                                if j!=i:weight*=pay[h,j] if a else 1-pay[h,j]
                            future[ownpay]+=weight*v[count*3+2,i]
                    pp=p[i,h,s,1]
                    expected_future=(1-pp)*future[0]+pp*future[1]
                    net=-.25*pp
                    pay_advantage=-.25+BETA*(future[1]-future[0])
                    wpay=d[h]*signal_prob*p[i,h,s,0]*pg
                    derivative=(1-epsilon)*base[i,h,s,1]*(1-base[i,h,s,1])
                    fisher[i,h,s,1]=wpay*derivative**2/(pp*(1-pp))
                    gradient[i,h,s,1]=wpay*derivative*pay_advantage
                    advantages[i,h,s,1]=pay_advantage
                else:
                    expected_future=0.
                    for mask in range(8):
                        weight=1.;count=0
                        for j in range(3):
                            a=(mask>>j)&1;count+=a
                            weight*=pay[h,j] if a else 1-pay[h,j]
                        expected_future+=weight*v[count*3+2,i]
                    net=.25*pay[h].sum()
                joint=AUT-.3*(i==3)+pg*(.8*F+net)-pb*(Y+losses[i])
                joint+=BETA*((1-pg-pb)*v[ha,i]+pb*v[hb,i]+pg*expected_future)
                alone=AUT+BETA*v[ha,i]
                advantage=joint-alone
                weight=d[h]*signal_prob
                derivative=(1-epsilon)*base[i,h,s,0]*(1-base[i,h,s,0])
                mix=p[i,h,s,0]
                fisher[i,h,s,0]=weight*derivative**2/(mix*(1-mix))
                gradient[i,h,s,0]=weight*derivative*advantage
                advantages[i,h,s,0]=advantage
    return gradient,fisher,advantages,v,d


@njit(cache=True)
def vector_field(flat,natural,epsilon=0.):
    theta=flat.reshape((4,15,2,2))
    clipped=np.minimum(12.,np.maximum(-12.,theta))
    grad,fisher,adv,v,d=gradients(clipped,np.array([1.,1.,7.,7.]),epsilon)
    field=grad.copy()
    for i in range(4):
        for h in range(15):
            for s in range(2):
                for head in range(2):
                    if natural:
                        field[i,h,s,head]=grad[i,h,s,head]/fisher[i,h,s,head] if fisher[i,h,s,head]>0 else 0.
                    x=theta[i,h,s,head];g=field[i,h,s,head]
                    if (x>=12 and g>0) or (x<=-12 and g<0):field[i,h,s,head]=0.
    return field.reshape(flat.size)


def initial(kind,seed=None):
    theta=np.zeros((4,15,2,2))
    if kind=='WARM':
        for i,loss in enumerate([1,1,7,7]):
            for h in range(15):
                active=h//3 in [2,3,4]
                for s in range(2):
                    mode=int(active and (loss==1 or s==1))
                    pay=int(active and i<3 and loss==1)
                    theta[i,h,s,0]=math.log(19.)*(2*mode-1)
                    theta[i,h,s,1]=math.log(19.)*(2*pay-1)
    elif kind=='JITTER':
        theta=np.random.Generator(np.random.Philox(seed)).normal(0,.001,theta.shape)
    elif kind!='COLD':raise ValueError(kind)
    return theta


def to_v202_probabilities(theta):
    return np.asarray(probability(theta)).reshape((4,30,2))


def history_spread(theta):
    # h=14 is the unreachable combination "no successful payment yet, GOOD".
    p=np.asarray(probability(theta))[:,:14]
    return float(np.max(np.ptp(p[:,:,:,0],axis=1))),float(np.max(np.ptp(p[:3,:,:,1],axis=1)))
