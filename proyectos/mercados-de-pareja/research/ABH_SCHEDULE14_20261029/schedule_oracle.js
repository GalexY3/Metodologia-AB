"use strict";
// Exact 2x2 institution-level encounter scheduler; synthetic, not empirical. Source frozen before outcomes.
function assert_(condition,msg){if(!condition)throw Error(msg);}

function approx(x,y,tol=1e-10){return Math.abs(x-y)<tol;}

function nbits(x){let n=0;while(x){n+=(x&1);x>>>=1;}return n;}

function exposurePolicies(){
  const uniformTwo={};for(const k of [3,5,6,9,10,12])uniformTwo[k]=1/6;
  const independent={};for(let m=0;m<16;m++)independent[m]=1/16;
  const rotation={6:.5,9:.5};
  const adjacent={3:.25,5:.25,10:.25,12:.25};
  function mixture(a,b,u=.9){const out={};for(let m=0;m<16;m++){const w=u*(a[m]||0)+(1-u)*(b[m]||0);if(w)out[m]=w;}return out;}
  return {independent,rotation,uniformTwo,adjacent,rotationMix:mixture(rotation,uniformTwo),adjacentMix:mixture(adjacent,uniformTwo)};
}

function maxMatchMasks(mask){
  const allowed=[];for(let c=0;c<16;c++){
    if((c&mask)!==c)continue;
    const noSharedRows=nbits(c&3)<=1 && nbits(c&12)<=1;
    const noSharedCols=nbits(c&5)<=1 && nbits(c&10)<=1;
    if(noSharedRows && noSharedCols)allowed.push(c);
  }
  const best=Math.max(...allowed.map(nbits));
  return allowed.filter(m=>nbits(m)===best).sort((a,b)=>b-a);
}

function canonicalMatch(mask){return maxMatchMasks(mask)[0];}

function exposureStats(policy){
 const total=Object.values(policy).reduce((a,b)=>a+b,0);
 const e=Array.from({length:4},(_,i)=>Object.entries(policy).reduce((s,[m,w])=>s+(Number(m)&(1<<i)?w:0),0));
 const e0e3=Object.entries(policy).reduce((s,[m,w])=>s+((Number(m)&9)===9?w:0),0);
 const aMean=e[0]+e[1];const aSecond=Object.entries(policy).reduce((s,[m,w])=>{const c=nbits(Number(m)&3);return s+w*c*c;},0);
 const p0=Object.entries(policy).reduce((s,[m,w])=>s+((Number(m)&3)===0?w:0),0);
 const nMean=Object.entries(policy).reduce((s,[m,w])=>s+w*nbits(Number(m)),0);
 const nSecond=Object.entries(policy).reduce((s,[m,w])=>s+w*nbits(Number(m))**2,0);
 return {mass:total,edge_exposure:e,total_exposures:nMean,variance_total:nSecond-nMean*nMean,actor0_exposure_mean:aMean,actor0_exposure_variance:aSecond-aMean*aMean,actor0_no_exposure_probability:p0,exposure_edge0_edge3_covariance:e0e3-e[0]*e[3]};
}

function exactOutcome(policy,p){
 assert_(p>=0&&p<=1,"p out of [0,1]");
 const count_distribution=[0,0,0],consent_masks=Array(16).fill(0);
 let mass=0,expectedMutual=0,expectedMatching=0;
 for(const [key,w] of Object.entries(policy)){
  const mask=Number(key),n=nbits(mask);
  for(let c=0;c<16;c++){
   if((c&mask)!==c)continue;
   const yes=nbits(c),prob=w*p**yes*(1-p)**(n-yes), k=nbits(canonicalMatch(c));
   count_distribution[k]+=prob;consent_masks[c]+=prob;
   expectedMutual+=prob*yes;expectedMatching+=prob*k;mass+=prob;
  }
 }
 return {mass,expected_mutual_edges:expectedMutual,expected_matching:expectedMatching,probability_2:count_distribution[2],probability_0:count_distribution[0],count_distribution,consent_masks};
}

function kl(P,Q){let k=0;assert_(P.length===Q.length,"KL dimensions");for(let i=0;i<P.length;i++)if(P[i]>0){assert_(Q[i]>0,"KL support mismatch");k+=P[i]*Math.log(P[i]/Q[i]);}return k;}

function dist16(policy){return Array.from({length:16},(_,i)=>policy[i]||0);}

function xorshift32(seed){let state=seed>>>0;return function(){state^=state<<13;state^=state>>>17;state^=state<<5;return (state>>>0)/4294967296;};}

function monteCarlo(policy,p,n,seed){
 const draw=xorshift32(seed),items=Object.entries(policy).map(([m,w])=>[Number(m),w]),hist=[0,0,0];
 for(let t=0;t<n;t++){
  let v=draw(),s=0,exposure=items[items.length-1][0];
  for(const [m,w] of items){s+=w;if(v<s){exposure=m;break;}}
  let yes=0;for(let i=0;i<4;i++)if(exposure&(1<<i)){if(draw()<p)yes|=1<<i;}
  const count=nbits(canonicalMatch(yes));assert_(count<=2,"capacity exceeded");hist[count]++;
 }
 return {seed,n,counts:hist,mean:(hist[1]+2*hist[2])/n,p2:hist[2]/n};
}

function runN93(){const a=exposurePolicies(),p=.5,stats={};for(const [k,v] of Object.entries(a)){const s=exposureStats(v),o=exactOutcome(v,p);assert_(approx(s.mass,1)&&approx(o.mass,1),`mass ${k}`);assert_(s.edge_exposure.every(x=>approx(x,.5)),`marginal ${k}`);stats[k]={...s,check_outcome_mass:o.mass};}return {status:"PASS",statistics:stats,next:"N94 independent vs coordinated rotation"};}

function runN94(){const {independent,rotation}=exposurePolicies();const i=exactOutcome(independent,.5),r=exactOutcome(rotation,.5);assert_(approx(i.expected_matching,.8046875),`indep ${i.expected_matching}`);assert_(approx(r.expected_matching,1)&&r.expected_matching>i.expected_matching,"rotation contrast failed");return {status:"PASS",independent_expected_matches:i.expected_matching,rotation_expected_matches:r.expected_matching,delta:r.expected_matching-i.expected_matching,rot_p2:r.probability_2,ind_p2:i.probability_2,warning:"Independent has variable total exposures; isolate fixed-cardinality in N95",next:"N95 budget-matched 2-exposure policy"};}

function runN95(){const {uniformTwo,rotation}=exposurePolicies();const a=exposureStats(uniformTwo),b=exposureStats(rotation),x=exactOutcome(uniformTwo,.5),y=exactOutcome(rotation,.5);assert_(approx(a.variance_total,0)&&approx(b.variance_total,0),"budget variance must be zero");assert_(approx(x.expected_matching,5/6)&&approx(y.expected_matching,1),"matched budget contrast");return {status:"PASS",uniform2_matches:x.expected_matching,rotation_matches:y.expected_matching,delta:y.expected_matching-x.expected_matching,exposure_budget:2,next:"N96 pure adjacent-overlap contrast"};}

function runN96(){const {adjacent,rotation}=exposurePolicies();const x=exactOutcome(adjacent,.5),y=exactOutcome(rotation,.5);assert_(approx(x.expected_matching,.75)&&approx(y.expected_matching,1)&&approx(y.expected_matching-x.expected_matching,.25),"congestion expected delta");return {status:"PASS",adjacent_matches:x.expected_matching,rotation_matches:y.expected_matching,delta:y.expected_matching-x.expected_matching,next:"N97 sensitivity across acceptance probabilities"};}

function runN97(){const {adjacent,rotation}=exposurePolicies();const cases=[];for(const p of [.1,.5,.9]){const x=exactOutcome(adjacent,p),y=exactOutcome(rotation,p),delta=y.expected_matching-x.expected_matching;assert_(approx(delta,p*p),`sensitivity p=${p}`);cases.push({p,adjacent:x.expected_matching,rotation:y.expected_matching,delta,formula:p*p});}return {status:"PASS",cases,next:"N98 actor-exposure count variance"};}

function runN98(){const {independent,rotation}=exposurePolicies();const a=exposureStats(independent),b=exposureStats(rotation);assert_(approx(a.actor0_exposure_mean,1)&&approx(b.actor0_exposure_mean,1),"actor mean");assert_(approx(a.actor0_exposure_variance,.5)&&approx(b.actor0_exposure_variance,0),"actor variance");assert_(approx(a.actor0_no_exposure_probability,.25)&&approx(b.actor0_no_exposure_probability,0),"actor zero");return {status:"PASS",independent:a,rotation:b,next:"N99 full count distribution"};}

function runN99(){const x=exposurePolicies(),r=exactOutcome(x.rotation,.5),u=exactOutcome(x.uniformTwo,.5),a=exactOutcome(x.adjacent,.5);assert_(approx(r.probability_2,.25)&&approx(u.probability_2,1/12)&&approx(a.probability_2,0),"P2 distribution");return {status:"PASS",p2_rotation:r.probability_2,p2_uniform2:u.probability_2,p2_adjacent:a.probability_2,distributions:{rotation:r.count_distribution,uniform2:u.count_distribution,adjacent:a.count_distribution},next:"N100 reparameterization of match rates"};}

function runN100(){const x=exposurePolicies(),pRot=.4,pAdj=1-Math.sqrt(.2),a=exactOutcome(x.rotation,pRot),b=exactOutcome(x.adjacent,pAdj);assert_(approx(a.expected_matching,.8)&&approx(b.expected_matching,.8),"match means not equal");assert_(a.probability_2>0&&approx(b.probability_2,0),"count distribution should differ");return {status:"PASS",p_rotation:pRot,p_adjacent:pAdj,matched_mean_rotation:a.expected_matching,matched_mean_adjacent:b.expected_matching,p2_rotation:a.probability_2,p2_adjacent:b.probability_2,next:"N101 maximum-cardinality tie-breaking and composition"};}

function runN101(){const choices=maxMatchMasks(15);assert_(choices.length===2&&choices.includes(9)&&choices.includes(6),"all 4 edges has exactly 2 perfect matchings");const same=[0,3],per=choices.map(m=>({mask:m,same_group_pairs:same.reduce((s,i)=>s+((m>>i)&1),0),cardinality:nbits(m)}));assert_(per.some(x=>x.same_group_pairs===2)&&per.some(x=>x.same_group_pairs===0)&&canonicalMatch(15)===9,"composition tie");return {status:"PASS",maxima:per,lexical_choice:canonicalMatch(15),next:"N102 randomized tie and group composition"};}

function runN102(){const choices=maxMatchMasks(15),same=x=>((x&1)?1:0)+((x&8)?1:0),uniform=choices.reduce((s,m)=>s+same(m),0)/choices.length,lex=same(canonicalMatch(15));assert_(approx(uniform,1)&&lex===2&&choices.every(m=>nbits(m)===2),"randomized tie");return {status:"PASS",expected_same_uniform_tie:uniform,same_lexical_tie:lex,matched_total:2,next:"N103 native bilateral data measurement"};}

function runN103(){const u=[.5,.5],v=[.25,1];assert_(approx(u[0]*u[1],v[0]*v[1]),"mutual disagree");assert_(!approx(u[0],v[0]),"unilateral same");return {status:"PASS",pair_mutual_probability:.25,world_uniform_actor_yes:.5,world_asymmetric_actor_yes:.25,world_asymmetric_counterpart_yes:1,next:"N104 joint distribution despite equal marginal q"};}

function runN104(){const x=exposurePolicies();const r=exactOutcome(x.rotation,.5),i=exactOutcome(x.independent,.5);const q0r=r.consent_masks.reduce((s,w,m)=>s+((m&1)?w:0),0),q0i=i.consent_masks.reduce((s,w,m)=>s+((m&1)?w:0),0),joint_r=r.consent_masks.reduce((s,w,m)=>s+((m&9)===9?w:0),0),joint_i=i.consent_masks.reduce((s,w,m)=>s+((m&9)===9?w:0),0);assert_(approx(q0r,.25)&&approx(q0i,.25),"q edge");assert_(approx(joint_r,.125)&&approx(joint_i,.0625),"joint pair");return {status:"PASS",q0_marginal_both:.25,joint_r,joint_i,covariance_rotation:joint_r-.25**2,covariance_independent:joint_i-.25**2,next:"N105 value of institution exposure logs"};}

function runN105(){const x=exposurePolicies(),a=dist16(x.rotationMix),b=dist16(x.adjacentMix),eA=exactOutcome(x.rotationMix,.5),eB=exactOutcome(x.adjacentMix,.5),KLe=kl(a,b),KLm=kl(eA.count_distribution,eB.count_distribution);assert_(KLe>KLm&&KLm>=0&&Number.isFinite(KLe)&&Number.isFinite(KLm),"information inequality");return {status:"PASS",kl_exposure_nats:KLe,kl_matching_count_nats:KLm,information_loss:KLe-KLm,policy_mixture:"90% structured, 10% fixed-two uniform",next:"N106 stochastic validation against exact finite target"};}

function runN106(){const x=exposurePolicies(),e=exactOutcome(x.rotation,.5),a=monteCarlo(x.rotation,.5,30000,20261029),b=monteCarlo(x.rotation,.5,30000,20261029);assert_(JSON.stringify(a)===JSON.stringify(b),"PRNG nonrepeat");assert_(Math.abs(a.mean-e.expected_matching)<.025&&Math.abs(a.p2-e.probability_2)<.02,"MC not within tolerance");return {status:"PASS",exact_mean:e.expected_matching,exact_p2:e.probability_2,monte_carlo:a,stochastic_reproducible:true,next:"STOP_R5 human remains; audit code portability and communicate theory as conditional mathematical argument"};}

function runAll(){return [runN93,runN94,runN95,runN96,runN97,runN98,runN99,runN100,runN101,runN102,runN103,runN104,runN105,runN106].map((fn,i)=>({cycle:"N"+(93+i),...fn()}));}
if(typeof require!=="undefined"&&typeof module!=="undefined"&&require.main===module)console.log(JSON.stringify(runAll(),null,2));
if(typeof module!=="undefined")module.exports={exposurePolicies,maxMatchMasks,exposureStats,exactOutcome,runAll};
