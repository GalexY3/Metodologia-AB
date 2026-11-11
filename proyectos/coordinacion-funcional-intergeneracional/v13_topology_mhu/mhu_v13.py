"""Finite-window MULTICOMPONENT spatial order diagnostics.

For each occupied profession j, at each nonzero low-frequency wavevector q,
compute |sum_{i:job_i=j} exp(-2πi q·x_i)|² relative to exact expectation for
RANDOMLY SHUFFLED labels with identical occupational counts and coordinates.
1 = conditional random marks; below 1 = suppressed low-q fluctuations;
above 1 = clustering. Neither finite suppression nor good food proves
strict multihyperuniformity, a thermodynamic-limit property.
"""
from __future__ import annotations
import numpy as np
from network_v13 import coordinates,grid_shape

MODES=np.array([(1,0),(0,1),(1,1),(1,-1),(2,0),(0,2)],dtype=int)

def low_phases(xy,modes=MODES):
    return np.exp(-2j*np.pi*np.asarray(xy)@np.asarray(modes,dtype=float).T)

def partial_spectrum(jobs,xy,min_count=4,modes=MODES):
    jobs=np.asarray(jobs,dtype=int).reshape(-1)
    xy=np.asarray(xy,float)
    n=len(jobs)
    if len(xy)!=n:raise ValueError('coordinates and jobs not same length')
    modes=np.asarray(modes,dtype=int)
    if np.any(np.all(modes==0,axis=1)):raise ValueError('zero wavevector forbidden')
    phases=low_phases(xy,modes)
    total_abs2=np.abs(phases.sum(0))**2
    per=[]
    for role in np.unique(jobs):
        sel=jobs==role
        count=int(sel.sum())
        if count<min_count or n-count<min_count:continue
        amp=np.abs(phases[sel].sum(0))**2
        # exact E_shuffle |sum_selected z_i|², sampling a fixed-size
        # subset WITHOUT replacement from the same fixed point support.
        expected=(count*(n-count)/(n-1)
            +count*(count-1)/(n*(n-1))*total_abs2)
        value=amp/np.maximum(expected,1e-12)
        per.append(dict(role=int(role),count=count,
                        score=float(value.mean()),max_mode=float(value.max()),
                        low_modes=[float(q) for q in value]))
    vals=np.array([r['score'] for r in per])
    return dict(mean_ratio=float(vals.mean()) if len(vals) else None,
         median_ratio=float(np.median(vals)) if len(vals) else None,
         max_component_ratio=float(vals.max()) if len(vals) else None,
         fraction_suppressed=float((vals<1).mean()) if len(vals) else None,
         n_resolved_components=len(vals),
         n_occupied=int(np.unique(jobs).size),
         modes=[list(map(int,x)) for x in modes],
         components=per)

def reference_balanced(n,m,k,xy,seed=0,kind='random',swaps=2500):
    """A quota-exact control: k equally frequent profession marks.
    kind='low_spectral' explicitly OPTIMIZES the same MHU diagnostic:
    positive-control ONLY, never evidence of emergent order or learning.
    """
    if n%k:raise ValueError('n must be divisible by k')
    rng=np.random.default_rng(seed)
    names=rng.choice(m,k,replace=False)
    ids=np.repeat(np.arange(k),n//k)
    rng.shuffle(ids)
    if kind=='random':return names[ids]
    if kind!='low_spectral':raise ValueError(kind)
    p=low_phases(xy)
    amps=np.stack([p[ids==r].sum(0) for r in range(k)])
    for _ in range(swaps):
        i,j=rng.choice(n,2,replace=False)
        u,v=ids[i],ids[j]
        if u==v:continue
        delta=p[j]-p[i]
        new_u=amps[u]+delta
        new_v=amps[v]-delta
        old=float((np.abs(amps[u])**2+np.abs(amps[v])**2).sum())
        new=float((np.abs(new_u)**2+np.abs(new_v)**2).sum())
        if new<old-1e-12:
            ids[i],ids[j]=v,u
            amps[u]=new_u;amps[v]=new_v
    return names[ids]

def aggregation(marks,xy):
    """Population-weighted sample scores across actual simulated societies."""
    data=[partial_spectrum(m,xy) for m in marks]
    resolved=[z for z in data if z['mean_ratio'] is not None]
    return dict(worlds=len(data),worlds_resolved=len(resolved),
        mean_ratio=float(np.mean([z['mean_ratio'] for z in resolved])) if resolved else None,
        median_ratio=float(np.median([z['mean_ratio'] for z in resolved])) if resolved else None,
        mean_max_component_ratio=float(np.mean([z['max_component_ratio'] for z in resolved])) if resolved else None,
        mean_frac_suppressed=float(np.mean([z['fraction_suppressed'] for z in resolved])) if resolved else None,
        mean_resolved_components=float(np.mean([z['n_resolved_components'] for z in data])),
        mean_occupied=float(np.mean([z['n_occupied'] for z in data])))

def calibration(n=120,m=10,k=4,seed=2201,reps=160):
    """Check exact count-matched shuffle null and intentionally regular marks."""
    xy=coordinates(n,'torus',seed)
    rng=np.random.default_rng(seed)
    random=[reference_balanced(n,m,k,xy,int(rng.integers(1e9))) for _ in range(reps)]
    ordered=[reference_balanced(n,m,k,xy,int(rng.integers(1e9)),
                 kind='low_spectral',swaps=1800) for _ in range(12)]
    return dict(null=aggregation(random,xy),
                constructed_positive_control=aggregation(ordered,xy),
                caveat='Ordered control is constructed by optimizing the reported observable; not an empirical neural discovery.')


def window_variance_ratio(jobs,xy,radii=(.16,.24,.32),grid_side=8,min_count=4):
    """Count variance relative to exact hypergeometric marking null, using
    circular windows on periodic 2-D domain at 64 translated centers.
    Added as exploratory cross-check of the earlier low-q spectral metric;
    finite windows do not establish an asymptotic scaling exponent.
    """
    labels=np.asarray(jobs,dtype=int)
    xy=np.asarray(xy,dtype=float)
    n=len(labels)
    active,identity=np.unique(labels,return_inverse=True)
    counts=np.bincount(identity)
    chosen=np.where((counts>=min_count)&(n-counts>=min_count))[0]
    if not len(chosen):return dict(mean_ratio=None,per_radius=[])
    marks=(identity[:,None]==chosen[None,:]).astype(float)
    jobsizes=counts[chosen].astype(float)
    grid=(np.arange(grid_side)+.5)/grid_side
    centers=np.array([(x,y) for x in grid for y in grid])
    delta=xy[None,:,:]-centers[:,None,:]
    delta-=np.round(delta)
    r2=(delta*delta).sum(2)
    items=[]
    for radius in radii:
        window=(r2<radius**2).astype(float)
        K=window.sum(1)
        valid=(K>0)&(K<n)
        X=window[valid]@marks
        k=K[valid,None]
        expected=k*jobsizes[None,:]/n
        variances=k*(jobsizes/n)[None,:]*(1-jobsizes/n)[None,:]*(n-k)/(n-1)
        ratios=np.sum((X-expected)**2,axis=0)/np.maximum(np.sum(variances,axis=0),1e-12)
        items.append(dict(radius=float(radius),
            mean_ratio=float(ratios.mean()),
            max_component_ratio=float(ratios.max()),
            components=[float(v) for v in ratios]))
    return dict(mean_ratio=float(np.mean([v['mean_ratio'] for v in items])),
                n_resolved_components=len(chosen),per_radius=items)
