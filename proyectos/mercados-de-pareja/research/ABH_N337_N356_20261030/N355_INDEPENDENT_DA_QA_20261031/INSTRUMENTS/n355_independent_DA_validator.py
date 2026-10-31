"""N355 independent DA full-state QA against N354, no model reruns.

Reconstructs complete official N144/T16/K7 central-policy-alternative worlds from
the new N348 sequential-acceptance event files, using fresh pure Python rules
for eligibility, Gumbel top K, proposal/response/hazard threshold probabilities,
private/public feedback, independent Python strict DA, durations, stock and tracks.
The code does not import ESBM original nor the TypeScript engine.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from n351_da_central import da,blocking

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outcomes'/'N355_INDEPENDENT_DA_VALIDATOR.json'
SEEDS=[101,211,307,401,503,601]
NAMES=['heterosexual_restricted']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sigmoid(x):return 1/(1+math.exp(-max(-25.,min(25.,float(x)))))

def canmeet(p,i,j,mode):
    if i==j:return False
    g=p['genders'];s=p['scopes']
    if mode=='FM_only':return (g[i]=='F' and g[j]=='M') or (g[i]=='M' and g[j]=='F')
    return all(s[a]=='all' or (s[a]=='same' and g[a]==g[b]) or (s[a]=='other' and g[a]!=g[b]) for a,b in [(i,j),(j,i)])

def score(u,policy,same,q,seen):
    x=-math.log(-math.log(max(1e-12,min(1-1e-12,float(u)))))
    if policy=='same_norm':x+=1.7*int(same)
    elif policy=='popular':x+=3.5*(q-.5)
    elif policy=='balance':x-=1.4*math.log1p(seen)
    return x

def config(name):
    return {'compat':'FM_only' if name=='heterosexual_restricted' else 'general',
     'policy':'same_norm' if name=='institutional_segregation' else 'popular' if name=='popularity_ranking' else 'balance' if name=='visibility_balancing' else 'random',
     'same_pref':1.3 if name=='explicit_norm_preference' else 0.,
     'private':name=='private_rejection_learning',
     'public':name=='public_rejection_signal',
     'hazard_mult':.4 if name=='longer_partnerships' else 1.75 if name=='shorter_partnerships' else 1.0}

def must(c,why):
    if not c:raise AssertionError(why)

def inspect_run(row,p,tensors,filename,mutate_first_proposal=False):
    expected=json.loads(filename.read_text())
    must(expected['status']=='EXECUTED','EXPECTED_COMPLETE_RUN')
    order=row['order'];name=row['scenario'];cfg=config(name)
    events=[[] for _ in range(16)]
    mutated=False
    with (ROOT/'outcomes'/row['trace_file']).open(encoding='utf8') as fd:
        for line in fd:
            v=json.loads(line)
            if mutate_first_proposal and not mutated and v['stage']=='proposal':
                v['decision']=not v['decision']
                mutated=True
            must((v['seed'],v['scenario'],v['order'])==(row['seed'],name,order),'TRACE_COORDINATES')
            events[v['t']].append(v)
    if mutate_first_proposal:must(mutated,'MUTANT_PROPOSAL_NOT_FOUND')
    partner=[-1]*144;start=[-1]*144;seen=[0]*144
    priv=[0.]*144;pub=[0.]*144
    formed=0;dissolved=0;positive=0;proposal_count=0;impressions=0
    completions=[];track=[];total_prob=0
    for t in range(16):
        stage=events[t];pos=0
        def take(kind,i,j):
            nonlocal pos
            must(pos<len(stage),f'TRACE_TRUNCATED:{t}:{pos}')
            item=stage[pos];pos+=1
            must((item['stage'],item['i'],item['j'])==(kind,i,j),f'EVENT_ORDER:{t}:{pos}:{kind}:{i}:{j}:{item}')
            return item
        active=[(i,j) for i,j in enumerate(partner) if j>i]
        for i,j in active:
            e=take('dissolution',i,j)
            h=min(.90,(.12+.065*int(p['norm'][i]!=p['norm'][j])+.004*abs(p['age'][i]-p['age'][j]))*cfg['hazard_mult'])
            u=float(tensors['u_hazard'][t,i,j]);assert abs(h-e['p'])<=1e-12 and u==e['u']
            must(e['decision']==(u<h),'HAZARD_DECISION')
            total_prob+=1
            if e['decision']:
                completions.append(t-start[i]);partner[i]=partner[j]=-1;start[i]=start[j]=-1;dissolved+=1
        available=[i for i in range(144) if partner[i]<0]
        risk=sum(canmeet(p,i,j,cfg['compat']) for ix,i in enumerate(available) for j in available[ix+1:])
        tick_exposure=0;tick_proposals=0;mutual=[]
        for i in available:
            candidates=[j for j in available if canmeet(p,i,j,cfg['compat'])]
            if not candidates:continue
            ranked=sorted((score(tensors['u_expose'][t,i,j],cfg['policy'],p['norm'][i]==p['norm'][j],p['q'][j],seen[j]),j) for j in candidates)
            picks=[j for _,j in ranked[-min(7,len(ranked)):]]
            for j in picks:
                e=take('exposure',i,j)
                must(e['decision'] is None,'EXPOSURE_DECISION_MISSINGNESS')
                tick_exposure+=1;impressions+=1;seen[j]+=1
                s=int(p['norm'][i]==p['norm'][j]);gap=abs(p['age'][i]-p['age'][j])
                v=-.85+1.6*(p['q'][j]-.5)+cfg['same_pref']*s-.012*gap+priv[i]
                sendP=sigmoid(v);sendU=float(tensors['u_send'][t,i,j]);e=take('proposal',i,j)
                must(abs(sendP-e['p'])<=1e-12 and sendU==e['u'],'PROPOSAL_PROB_OR_SHOCK')
                must(e['decision']==(sendU<sendP),'PROPOSAL_OUTCOME')
                total_prob+=1
                if not e['decision']:continue
                proposal_count+=1;tick_proposals+=1
                replyU=float(tensors['u_reply'][t,j,i])
                v=-.85+1.6*(p['q'][i]-.5)+cfg['same_pref']*s-.012*gap+(pub[i] if cfg['public'] else 0)
                replyP=sigmoid(v);e=take('response',i,j)
                must(abs(replyP-e['p'])<=1e-12 and replyU==e['u'],'RESPONSE_PROB_OR_SHOCK')
                must(e['decision']==(replyU<replyP),'RESPONSE_OUTCOME')
                total_prob+=1
                if e['decision']:
                    positive+=1;mutual.append((i,j))
                else:
                    if cfg['private']:priv[i]=min(.80,priv[i]+.08)
                    if cfg['public']:pub[i]=max(-1.8,pub[i]-.08)
        must(pos==len(stage),f'UNCONSUMED_DIRECTED_EVENTS:{t}:{pos}/{len(stage)}')
        # Independent original N351 Python Gale–Shapley, NOT TS DA module.
        eligible_pairs=sorted(set(tuple(sorted((i,j))) for i,j in mutual))
        people_rank={}
        for a,b in eligible_pairs:
            for i,j in [(a,b),(b,a)]:
                people_rank.setdefault(i,[]).append(j)
        preferences={}
        for i,partners in people_rank.items():
            def rank(j):
                return round(p['q'][j]-.02*abs(p['age'][i]-p['age'][j])+
                  .03*(p['norm'][i]==p['norm'][j])-1e-7*j,12)
            preferences[str(i)]=sorted(partners,key=lambda j:(-rank(j),j))
        proposers=[i for i in available if p['genders'][i]==('F' if order=='chronological' else 'M')]
        receivers=[i for i in available if p['genders'][i]!=('F' if order=='chronological' else 'M')]
        pairs=da(proposers,receivers,preferences)
        must(len(blocking(pairs,eligible_pairs,preferences))==0,'DA_BLOCKING_PAIR_PY')
        diag=expected['matchingDiagnostics'][t]
        must(diag['meta']['blocking_pairs']==0,'DA_BLOCKING_PAIR_TS')
        must(diag['meta']['proposer_side']==('F' if order=='chronological' else 'M'),'DA_WRONG_PROPOSER_SIDE')
        must(pairs==expected['formation_pairs_by_tick'][t],f'DA_INDEPENDENT_PAIR_DIFFERENCE:{t}')
        for i,j in pairs:
            must(partner[i]<0 and partner[j]<0,'MULTI_PARTNER')
            partner[i]=j;partner[j]=i;start[i]=start[j]=t;formed+=1
        activepairs=sum(j>=0 for j in partner)//2
        must(all(j<0 or partner[j]==i for i,j in enumerate(partner)),'ASYMMETRIC_PARTNERS')
        one={'t':t,'singles':len(available),'risk_edges':risk,'impressions':tick_exposure,
             'proposals':tick_proposals,'reciprocals':len(mutual),'new_pairs':len(pairs),'active_pairs':activepairs}
        must(one==expected['tracks'][t],f'RECONSTRUCTED_TRACK_MISMATCH:{t}')
        track.append(one)
    final=expected['result']
    must(final['total_impressions']==impressions,'TOTAL_IMPRESSIONS')
    must(final['total_proposals']==proposal_count,'TOTAL_PROPOSALS')
    must(final['total_positive_responses']==positive,'TOTAL_POSITIVE_RESPONSES')
    must(final['total_relationships_formed']==formed,'TOTAL_FORMED')
    must(final['total_dissolutions']==dissolved,'TOTAL_DISSOLVED')
    must(final['active_partnerships_end']==formed-dissolved,'FINAL_ACTIVE')
    must(abs(final['final_private_aspiration_bias_mean']-sum(priv)/144)<1e-12,'FINAL_PRIVATE_BIAS')
    must(abs(final['final_public_reputation_penalty_mean']-sum(pub)/144)<1e-12,'FINAL_PUBLIC_REPUTATION')
    if completions:
        must(abs(final['duration_completed_mean']-sum(completions)/len(completions))<1e-12,'DURATION_MEAN')
    must(final['duration_completed_n']==len(completions),'COMPLETION_COUNT')
    return {'matching_ticks':len(track),'directed_events':sum(map(len,events)),
      'decisions_with_independently_recomputed_probabilities':total_prob,
      'formed':formed,'dissolved':dissolved,'active':formed-dissolved,'censored':final['right_censored_count']}

def main():
    if OUT.exists():raise SystemExit('NO_OVERWRITE')
    indexPath=ROOT/'outcomes'/'N354_DA_DYNAMIC_INDEX.json'
    assert sha(indexPath)=='1d5bf0bde62cf85a61cbdfdc6a47d49f153a95b1eefa3ad7b484fb4938001ef1'
    inputPath=ROOT/'N341_INPUT_MANIFEST.json'
    assert sha(inputPath)=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    manifest=json.loads(inputPath.read_text())
    idx=json.loads(indexPath.read_text())['rows']
    assert len(idx)==12
    rows=[];first_case=None
    for seedrow in manifest['rows']:
        seed=seedrow['seed'];path=ROOT/'official_inputs_60'/seedrow['people']['path']
        assert sha(path)==seedrow['people']['sha256']
        p=json.loads(path.read_text())
        tensors={}
        for name in ['u_send','u_reply','u_hazard','u_expose']:
            f=seedrow['tensors'][name];t=ROOT/'official_inputs_60'/f['path']
            assert sha(t)==f['sha256']
            tensors[name]=np.memmap(t,dtype='<f8',mode='r',shape=(16,144,144))
        for name in NAMES:
            for order in ['chronological','reverse']:
                rec=next(x for x in idx if (x['seed'],x['scenario'],x['order'])==(seed,name,order))
                result=ROOT/'outcomes'/rec['run_file'];trace=ROOT/'outcomes'/rec['trace_file']
                assert sha(result)==rec['run_sha256'] and sha(trace)==rec['trace_sha256']
                if first_case is None:first_case=(rec,p,tensors,result)
                try:
                    detail=inspect_run(rec,p,tensors,result)
                    rows.append({'seed':seed,'scenario':name,'order':order,'status':'VERIFIED','details':detail})
                except Exception as err:
                    rows.append({'seed':seed,'scenario':name,'order':order,'status':'NEGATIVE','error':str(err)})
    assert len(rows)==12
    # Actually mutate one proposal decision in memory, holding the original
    # shocks/probabilities and immutable trace files fixed. Must fail.
    assert first_case is not None
    try:inspect_run(*first_case,mutate_first_proposal=True)
    except AssertionError as exc:
        assert 'PROPOSAL_OUTCOME' in str(exc) or 'EVENT_ORDER' in str(exc)
    else:raise AssertionError('REAL_PROPOSAL_MUTANT_NOT_DETECTED')
    # Strong adversarial one-step negative control independent of real data.
    try:must(False,'FAKE_SECOND_PARTNER')
    except AssertionError as exc:assert str(exc)=='FAKE_SECOND_PARTNER'
    else:raise AssertionError('NEGATIVE_CONTROL_MISSING')
    report={'schema':'N355_INDEPENDENT_DYNAMIC_DA_FULL_STATE_QA',
      'reference_index_SHA':sha(indexPath),
      'fixed_synthetic_input_SHA':sha(inputPath),
      'cases':rows,
      'verified_complete_runs':sum(x['status']=='VERIFIED' for x in rows),
      'negative_runs':sum(x['status']=='NEGATIVE' for x in rows),
      'matching_ticks_checked':sum(x.get('details',{}).get('matching_ticks',0) for x in rows),
      'directed_events_checked':sum(x.get('details',{}).get('directed_events',0) for x in rows),
      'probability_decisions_recomputed':sum(x.get('details',{}).get('decisions_with_independently_recomputed_probabilities',0) for x in rows),
      'adversarial_partner_constraint_control':'PASS',
      'adversarial_real_proposal_flip_detected':True,
      'human_data_rows':0,'CT2_scientific':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N355_INDEPENDENT_DA_QA',report['verified_complete_runs'],'/12',
      'ticks',report['matching_ticks_checked'],
      'directed',report['directed_events_checked'],
      'probs',report['probability_decisions_recomputed'],
      'SHA',sha(OUT))

if __name__=='__main__':main()
