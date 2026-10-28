"""ABR-BRANCH8-20261028: locked synthetic tests N01-N05 (not human data).
Requires numpy. All outcomes follow PREREG.json committed before scientific runs.
"""
import csv, json, argparse, hashlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).parent
SEEDS=[202,404,606]
Q0=.9; FATIGUE=.0025; BETA=.01; FLOOR=.05


def population(nm,nw,seed):
    rng=np.random.default_rng(seed)
    sm,bm,sw,bw=(rng.random(z) for z in (nm,nm,nw,nw))
    vm=.6*sm+.4*bm # man's value to female evaluators
    vw=.4*sw+.6*bw # woman's value to male evaluators
    return rng,sm,bm,sw,bw,vm,vw


def metrics(mate,vm,vw,when=None,sm=None,sw=None):
    m=np.flatnonzero(mate>=0); w=mate[m]; nm=len(mate); nw=len(vw)
    ans=dict(pairs=len(m),coverage=2*len(m)/(nm+nw),coverage_m=len(m)/nm,coverage_w=len(m)/nw,
             r_value=float(np.corrcoef(vm[m],vw[w])[0,1]) if len(m)>2 else None,
             median_gap=float(np.median(np.abs(vm[m]-vw[w]))) if len(m) else None,
             median_round=float(np.median(when[m])) if when is not None and len(m) else None)
    if sm is not None and len(m)>2:ans['r_status']=float(np.corrcoef(sm[m],sw[w])[0,1])
    return ans


def stream(nm,nw,seed,T=180,beta=BETA,idio=.0,cutoff=0.05,record=False):
    rng,sm,bm,sw,bw,vm,vw=population(nm,nw,seed)
    # Fixed personal tastes for N01; independent for each directed appraisal.
    u_m=np.clip(vw[None,:]+rng.normal(0,idio,(nm,nw)),0,1)
    u_w=np.clip(vm[:,None]+rng.normal(0,idio,(nm,nw)),0,1)
    active_m=np.ones(nm,bool);active_w=np.ones(nw,bool);q_m=np.full(nm,Q0);q_w=np.full(nw,Q0)
    mate=np.full(nm,-1,int);when=np.full(nm,-1,int)
    log=[];qcheck=[];events=[]
    for t in range(1,T+1):
        m=np.flatnonzero(active_m);w=np.flatnonzero(active_w)
        if not len(m) or not len(w):break
        rng.shuffle(m);rng.shuffle(w); k=min(len(m),len(w));m=m[:k];w=w[:k]
        rm=(u_m[m,w]>=np.maximum(q_m[m],cutoff));rw=(u_w[m,w]>=np.maximum(q_w[w],cutoff))
        yes=rm&rw;mm=m[yes];ww=w[yes]
        active_m[mm]=False;active_w[ww]=False;mate[mm]=ww;when[mm]=t
        bad=~yes;mi=m[bad];wi=w[bad];a=rm[bad];b=rw[bad]
        q_m[mi]=np.maximum(FLOOR,q_m[mi]-FATIGUE-beta*(a&~b))
        q_w[wi]=np.maximum(FLOOR,q_w[wi]-FATIGUE-beta*(b&~a))
        if record:
            log.append(dict(round=t,men_at_risk=int(len(m)),women_at_risk=int(len(w)),matches=int(len(mm))))
            if t in (30,90,150):qcheck.append(dict(round=t,q_m_active_median=float(np.median(q_m[active_m])) if active_m.any() else None,q_w_active_median=float(np.median(q_w[active_w])) if active_w.any() else None))
            for mid,wid in zip(mm,ww):events.append((t,int(mid),int(wid)))
    return dict(mate=mate,when=when,vm=vm,vw=vw,u_m=u_m,u_w=u_w,log=log,qcheck=qcheck,events=events,sm=sm,sw=sw,**metrics(mate,vm,vw,when,sm,sw))


def gs(um,uw,cutoff=.05):
    nm,nw=um.shape
    # Men propose in descending utility; women retain the best acceptable proposer.
    rankings=np.argsort(-um,axis=1,kind='stable');pos=np.zeros(nm,int);wife=np.full(nm,-1,int);husband=np.full(nw,-1,int)
    queue=list(range(nm));proposals=0
    while queue:
        m=queue.pop(0)
        while pos[m]<nw:
            w=int(rankings[m,pos[m]]);pos[m]+=1
            if um[m,w]<cutoff:break
            proposals+=1
            if uw[m,w]<cutoff:continue
            old=husband[w]
            if old==-1 or uw[m,w]>uw[old,w]:
                husband[w]=m;wife[m]=w
                if old!=-1:
                    wife[old]=-1;queue.append(int(old))
                break
    return wife,proposals


def blocking_pairs(mate,um,uw,cutoff=.05):
    nm,nw=um.shape
    wives=mate
    husbands=np.full(nw,-1,int)
    for m,w in enumerate(wives):
        if w>=0:husbands[w]=m
    own_m=np.array([um[m,w] if w>=0 else cutoff for m,w in enumerate(wives)])
    own_w=np.array([uw[m,w] if m>=0 else cutoff for w,m in enumerate(husbands)])
    superior=(um>own_m[:,None]+1e-12)&(uw>own_w[None,:]+1e-12)&(um>=cutoff)&(uw>=cutoff)
    return int(superior.sum())


def n01(seed):
    nm=nw=200
    r=stream(nm,nw,seed,T=180,idio=.08)
    wgs,proposals=gs(r['u_m'],r['u_w'])
    rows=[]
    for name,mate,when in [('sequential',r['mate'],r['when']),('deferred_acceptance',wgs,None)]:
        d=metrics(mate,r['vm'],r['vw'],when);d.update(cycle='N01',seed=seed,variant=name,
                 blocking_pairs=blocking_pairs(mate,r['u_m'],r['u_w']),proposals=proposals if name=='deferred_acceptance' else None)
        rows.append(d)
    assert rows[1]['blocking_pairs']==0 and len(np.unique(wgs[wgs>=0]))==np.sum(wgs>=0)
    return rows


def n02(seed):
    out=[];haz=[];qs=[]
    for name,beta in [('fatigue_only',0.),('rejection_feedback',BETA)]:
        r=stream(600,600,seed,T=180,beta=beta,record=True)
        d={k:r[k] for k in ('pairs','coverage','coverage_m','coverage_w','r_value','median_gap','median_round')}
        d.update(cycle='N02',seed=seed,variant=name);out.append(d)
        for sex,vals,match_round in [('men',r['vm'],r['when']),('women',r['vw'],None)]:
            if sex=='women':
                # derive when from matched men indexes
                match_round=np.full(600,-1,int)
                for i,w in enumerate(r['mate']):
                    if w>=0:match_round[w]=r['when'][i]
            dec=np.minimum((np.argsort(np.argsort(vals))*10//len(vals))+1,10)
            for rank in (1,5,10):
                for start,end in [(1,60),(61,120),(121,180)]:
                    mask=(dec==rank);at_risk=mask&((match_round<0)|(match_round>=start));n_risk=int(at_risk.sum()); n_match=int((mask&(match_round>=start)&(match_round<=end)).sum())
                    haz.append(dict(cycle='N02',seed=seed,variant=name,sex=sex,decile=rank,period=f'{start}-{end}',risk_at_start=n_risk,matches_in_interval=n_match,cumulative_interval_probability=n_match/n_risk if n_risk else None))
        qs.extend(dict(cycle='N02',seed=seed,variant=name,**x) for x in r['qcheck'])
    return out,haz,qs


def n03(seed):
    base_rng,sm,bm,sw,bw,vm,vw=population(600,600,seed)
    rows=[];distinct_audit=[]
    for pool_total in (100,300,1200):
        per_side=pool_total//2
        # same agents/attributes, random disjoint but sex-balanced memberships.
        rand=np.random.default_rng(seed+pool_total*991)
        male_order=rand.permutation(600).reshape(-1,per_side)
        female_order=rand.permutation(600).reshape(-1,per_side)
        active_m=np.ones(600,bool);active_w=np.ones(600,bool); q_m=np.full(600,Q0);q_w=np.full(600,Q0)
        mate=np.full(600,-1,int);seen=set();repeat=0;potential=0;actual=0;when=np.full(600,-1,int)
        for t in range(20):
            # Unique round-robin profile across every participant, independent of match attrition
            m=male_order.ravel();w=np.concatenate([np.roll(group,t) for group in female_order]);
            all_pairs=list(zip(m.tolist(),w.tolist()));
            repeat+=sum((int(i),int(j)) in seen for i,j in all_pairs)
            seen.update(all_pairs);potential+=len(all_pairs)
            live=active_m[m]&active_w[w];m=m[live];w=w[live];actual+=len(m)
            am=vw[w]>=q_m[m];aw=vm[m]>=q_w[w];both=am&aw
            mi=m[both];wi=w[both];active_m[mi]=False;active_w[wi]=False;mate[mi]=wi;when[mi]=t+1
            mfail=m[~both];wfail=w[~both];a=am[~both];b=aw[~both]
            q_m[mfail]=np.maximum(FLOOR,q_m[mfail]-FATIGUE-BETA*(a&~b))
            q_w[wfail]=np.maximum(FLOOR,q_w[wfail]-FATIGUE-BETA*(b&~a))
        assert repeat==0 and len(np.unique(mate[mate>=0]))==sum(mate>=0)
        d=metrics(mate,vm,vw,when);d.update(cycle='N03',seed=seed,variant=f'balanced_pool_{pool_total}',distinct_profiles_repeated=repeat,
                                          scheduled_exposures=potential,effective_exposures=actual,unique_ratio=1.0)
        rows.append(d)
    return rows


def async_one(seed,expiry):
    nm=nw=300; T=100
    rng,sm,bm,sw,bw,vm,vw=population(nm,nw,seed)
    seen_m=np.zeros((nm,nw),bool);seen_w=np.zeros((nm,nw),bool)
    likes_m=np.full((nm,nw),-1,int); likes_w=np.full((nm,nw),-1,int)
    am=np.ones(nm,bool);aw=np.ones(nw,bool);q_m=np.full(nm,Q0);q_w=np.full(nw,Q0);mate=np.full(nm,-1,int); when=np.full(nm,-1,int)
    # Permutations fixed before the first tick; attrition merely skips removed profiles.
    feed_m=np.stack([rng.permutation(nw) for _ in range(nm)])
    feed_w=np.stack([rng.permutation(nm) for _ in range(nw)])
    pointer_m=np.zeros(nm,int);pointer_w=np.zeros(nw,int)
    views=likes=mutual_candidates=0;exposures_for_each_m=np.zeros(nm,int);exposures_for_each_w=np.zeros(nw,int)
    for t in range(1,T+1):
        # Men and women each view one unseen candidate per tick; order alternates to limit first-mover bias
        for sex in ('men','women') if t%2 else ('women','men'):
            if sex=='men':
                ids=np.flatnonzero(am);rng.shuffle(ids)
                for i in ids:
                    if not am[i]:continue
                    while pointer_m[i]<nw and not aw[feed_m[i,pointer_m[i]]]:pointer_m[i]+=1
                    if pointer_m[i]>=nw:continue
                    j=int(feed_m[i,pointer_m[i]]);pointer_m[i]+=1;seen_m[i,j]=True;views+=1;exposures_for_each_m[i]+=1
                    like=vw[j]>=q_m[i]
                    q_m[i]=max(FLOOR,q_m[i]-FATIGUE)
                    if like:
                        likes+=1;likes_m[i,j]=t
                        if likes_w[i,j]>=0 and (expiry is None or t-likes_w[i,j]<=expiry):
                            mutual_candidates+=1
                            am[i]=False;aw[j]=False;mate[i]=j;when[i]=t
                    elif likes_w[i,j]>=0:q_w[j]=max(FLOOR,q_w[j]-BETA)
            else:
                ids=np.flatnonzero(aw);rng.shuffle(ids)
                for j in ids:
                    if not aw[j]:continue
                    while pointer_w[j]<nm and not am[feed_w[j,pointer_w[j]]]:pointer_w[j]+=1
                    if pointer_w[j]>=nm:continue
                    i=int(feed_w[j,pointer_w[j]]);pointer_w[j]+=1;seen_w[i,j]=True;views+=1;exposures_for_each_w[j]+=1
                    like=vm[i]>=q_w[j];q_w[j]=max(FLOOR,q_w[j]-FATIGUE)
                    if like:
                        likes+=1;likes_w[i,j]=t
                        if likes_m[i,j]>=0 and (expiry is None or t-likes_m[i,j]<=expiry):
                            mutual_candidates+=1
                            am[i]=False;aw[j]=False;mate[i]=j;when[i]=t
                    elif likes_m[i,j]>=0:q_m[i]=max(FLOOR,q_m[i]-BETA)
    assert np.all(seen_m.sum(1)<=T) and np.all(seen_w.sum(0)<=T) and np.sum(mate>=0)==mutual_candidates
    d=metrics(mate,vm,vw,when);d.update(cycle='N04',seed=seed,variant=f'async_expiry_{expiry}' if expiry is not None else 'async_persistent',views=views,likes=likes,mutual_candidates=mutual_candidates,unique_view_invariant=True)
    return d


def n04(seed):
    # simultaneous comparator uses same population construction but different directed opportunity budgets
    r=stream(300,300,seed,T=100,record=False)
    baseline={k:r[k] for k in ('pairs','coverage','coverage_m','coverage_w','r_value','median_gap','median_round')};baseline.update(cycle='N04',seed=seed,variant='simultaneous_repeating',views=None,likes=None,mutual_candidates=None,unique_view_invariant=None)
    return [baseline,async_one(seed,None),async_one(seed,20)]


def n05(seed,visibility):
    nm=nw=300;T=150;delta=.002
    rng,sm,bm,sw,bw,vm,vw=population(nm,nw,seed)
    group_m=rng.integers(0,4,nm);group_w=rng.integers(0,4,nw)
    # local reputations are directed view values, not changes to education/income.
    seen_m=np.broadcast_to(sm[None,:],(nw,nm)).copy() # female observer -> male subject
    seen_w=np.broadcast_to(sw[None,:],(nm,nw)).copy() # male observer -> female subject
    am=np.ones(nm,bool);aw=np.ones(nw,bool);q_m=np.full(nm,Q0);q_w=np.full(nw,Q0)
    mate=np.full(nm,-1,int);when=np.full(nm,-1,int);rejections=0;updates=0
    for t in range(1,T+1):
        m=np.flatnonzero(am);w=np.flatnonzero(aw)
        if not len(m) or not len(w):break
        rng.shuffle(m);rng.shuffle(w);k=min(len(m),len(w));m=m[:k];w=w[:k]
        util_m=.4*seen_w[m,w]+.6*bw[w]
        util_w=.6*seen_m[w,m]+.4*bm[m]
        right_m=util_m>=q_m[m]; right_w=util_w>=q_w[w]
        both=right_m&right_w;mm=m[both];ww=w[both];mate[mm]=ww;when[mm]=t;am[mm]=False;aw[ww]=False
        f=~both;mfail=m[f];wfail=w[f];rm=right_m[f];rw=right_w[f]
        q_m[mfail]=np.maximum(FLOOR,q_m[mfail]-FATIGUE-BETA*(rm&~rw));q_w[wfail]=np.maximum(FLOOR,q_w[wfail]-FATIGUE-BETA*(rw&~rm))
        male_rejected=mfail[rm&~rw];female_rejector=wfail[rm&~rw]
        female_rejected=wfail[rw&~rm];male_rejector=mfail[rw&~rm]
        rejections+=len(male_rejected)+len(female_rejected)
        for rejected,rejector in zip(male_rejected,female_rejector):
            if visibility=='none':continue
            if visibility=='private':aud=np.array([rejector])
            elif visibility=='random10':aud=rng.choice(nw,size=30,replace=False)
            else:aud=np.arange(nw)
            seen_m[aud,rejected]=np.maximum(0,seen_m[aud,rejected]-delta);updates+=len(aud)
        for rejected,rejector in zip(female_rejected,male_rejector):
            if visibility=='none':continue
            if visibility=='private':aud=np.array([rejector])
            elif visibility=='random10':aud=rng.choice(nm,size=30,replace=False)
            else:aud=np.arange(nm)
            seen_w[aud,rejected]=np.maximum(0,seen_w[aud,rejected]-delta);updates+=len(aud)
    assert len(np.unique(mate[mate>=0]))==sum(mate>=0)
    d=metrics(mate,vm,vw,when);d.update(cycle='N05',seed=seed,variant=visibility,rejection_events=rejections,observer_updates=updates,mean_seen_male_status=float(seen_m.mean()),mean_seen_female_status=float(seen_w.mean()))
    return d


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--test-only',action='store_true');a=ap.parse_args()
    # deterministic instrumentation checks, no experimental outcomes
    rng=np.random.default_rng(1);um=rng.random((7,7));uw=rng.random((7,7));wife,_=gs(um,uw)
    assert blocking_pairs(wife,um,uw)==0 and len(set(wife[wife>=0]))==sum(wife>=0)
    if a.test_only:
        print('DIAGNOSTIC_OK: GS stable/injective, source can be frozen before scientific runs');return
    main_rows=[];hazards=[];qs=[]
    for seed in SEEDS:
        main_rows+=n01(seed)
        o,h,q=n02(seed);main_rows+=o;hazards+=h;qs+=q
        main_rows+=n03(seed)
        main_rows+=n04(seed)
        for mode in ('none','private','random10','public'):
            main_rows.append(n05(seed,mode))
        print('FINISHED_SEED',seed,flush=True)
    def save(rows,path):
        if not rows:return
        keys=sorted(set().union(*[r.keys() for r in rows]));
        with open(HERE/path,'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    save(main_rows,'RESULTS.csv');save(hazards,'HAZARDS.csv');save(qs,'Q_TRACK.csv')
    print('RUNS',len(main_rows),'HAZARD_ROWS',len(hazards),'QROWS',len(qs))
    print('SUMMARY')
    for v in sorted(set(r['variant'] for r in main_rows)):
        rs=[r for r in main_rows if r['variant']==v];print(v,'coverage',np.mean([x['coverage'] for x in rs]),'r',np.mean([x['r_value'] for x in rs if x['r_value'] is not None]))
if __name__=='__main__': main()
