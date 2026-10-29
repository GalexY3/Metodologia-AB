"use strict";
/* AB-P exact micro-world reference, independent toy oracle, NOT human data, NOT ESBM v2 modification. */
function insist(cond,msg){ if(!cond) throw Error(msg); }

function maximumMatching(edges){
  let best=[]; const n=edges.length;
  for(let mask=0;mask<(1<<n);mask++){
    const left=new Set(),right=new Set(),selected=[];let valid=true;
    for(let i=0;i<n;i++) if(mask & (1<<i)){
      const [a,b]=edges[i];if(left.has(a)||right.has(b)){valid=false;break;}
      left.add(a);right.add(b);selected.push(edges[i]);
    }
    if(valid && selected.length>best.length) best=selected;
  }
  return best;
}

function greedyMatching(edges){
  let L=new Set(),R=new Set(),picked=[];
  for(const [a,b] of edges){if(!L.has(a)&&!R.has(b)){L.add(a);R.add(b);picked.push([a,b]);}}
  return picked;
}

function distribution(q){
  const EDGES=[[0,0],[0,1],[1,0],[1,1]];
  insist(q.length===EDGES.length && q.every(x=>x>=0&&x<=1),"Invalid q");
  const out={};let mass=0,expectedMutual=0,expectedMatches=0;
  for(let mask=0;mask<16;mask++){
    let probability=1;const live=[];
    for(let i=0;i<4;i++){
      const yes=!!(mask&(1<<i));probability*=yes?q[i]:1-q[i];if(yes)live.push(EDGES[i]);
    }
    const matched=maximumMatching(live);
    const key=matched.map(([a,b])=>`${a}${b}`).sort().join(",")||"none";
    out[key]=(out[key]||0)+probability;
    mass+=probability;expectedMutual+=probability*live.length;expectedMatches+=probability*matched.length;
  }
  return {mass,expectedMutual,expectedMatches,signatureDistribution:out};
}

function worldQ(world){
 return world.exposure.map((e,i)=>e*world.proposal[i]*world.response[i]);
}

function runP01(){
  const d=distribution([.2,.05,.05,.2]);
  insist(Math.abs(d.mass-1)<1e-12,"Mass not normalized");
  insist(d.expectedMatches>=0 && d.expectedMatches<=2,"Invalid cap");
  insist(d.expectedMutual>=d.expectedMatches,"Violation of matching capacity");
  return {status:"PASS",support:"Exact exhaustive 16 yes/no states; capacity invariants",mass:d.mass,expected_mutual_edges:d.expectedMutual,expected_formed_pairs:d.expectedMatches,distinct_final_matching_signatures:Object.keys(d.signatureDistribution).length,next:"P02 observational equivalence (structural exposure vs choice)"};
}

function runP02(){
  const A={exposure:[.8,.2,.2,.8],proposal:[.5,.5,.5,.5],response:[.5,.5,.5,.5]};
  const B={exposure:[.5,.5,.5,.5],proposal:[Math.sqrt(.4),Math.sqrt(.1),Math.sqrt(.1),Math.sqrt(.4)],response:[Math.sqrt(.4),Math.sqrt(.1),Math.sqrt(.1),Math.sqrt(.4)]};
  const qA=worldQ(A),qB=worldQ(B);insist(qA.every((x,i)=>Math.abs(x-qB[i])<1e-12),"q differs");
  const dA=distribution(qA),dB=distribution(qB);
  const keys=new Set([...Object.keys(dA.signatureDistribution),...Object.keys(dB.signatureDistribution)]);
  const tv=.5*[...keys].reduce((s,k)=>s+Math.abs((dA.signatureDistribution[k]||0)-(dB.signatureDistribution[k]||0)),0);
  insist(tv<1e-12,"Matching observations differ");
  return {status:"PASS",support:"Different stagewise structural mechanisms give indistinguishable entire match-set distribution",q_by_edges:qA,full_matching_distribution_TVD:tv,expected_final_pairs:dA.expectedMatches,next:"P03 audit which stage-specific logs distinguish these worlds"};
}

function runP03(){
  const A={exposure:[.8,.2,.2,.8],proposal:[.5,.5,.5,.5],response:[.5,.5,.5,.5]};
  const B={exposure:[.5,.5,.5,.5],proposal:[Math.sqrt(.4),Math.sqrt(.1),Math.sqrt(.1),Math.sqrt(.4)],response:[Math.sqrt(.4),Math.sqrt(.1),Math.sqrt(.1),Math.sqrt(.4)]};
  function stage(x){return {total_exposures:x.exposure.reduce((a,b)=>a+b,0),same_group_exposures:x.exposure[0]+x.exposure[3],cross_group_exposures:x.exposure[1]+x.exposure[2],expected_proposals:x.exposure.reduce((a,e,i)=>a+e*x.proposal[i],0),expected_mutual_edges:worldQ(x).reduce((a,b)=>a+b,0)};}
  const sA=stage(A),sB=stage(B);
  insist(Math.abs(sA.total_exposures-sB.total_exposures)<1e-12,"Total exposures differ");
  insist(Math.abs(sA.same_group_exposures-sB.same_group_exposures)>.25,"Stage-specific observation not discriminating");
  insist(Math.abs(sA.expected_mutual_edges-sB.expected_mutual_edges)<1e-12,"Mutual differs");
  return {status:"PASS",support:"Aggregate exposures and entire match distribution fail to distinguish; group-typed opportunity logs distinguish constructed worlds",world_exposure_segregated:sA,world_preference_segregated:sB,next:"P04 congestion and competent matching baseline"};
}

function runP04(){
  const adversarial=[[0,0],[0,1],[1,0]];
  const greedy=greedyMatching(adversarial).length,optimal=maximumMatching(adversarial).length;
  const saturated=distribution([1,1,1,1]);
  insist(greedy===1 && optimal===2,"Counterexample failed");
  insist(saturated.expectedMutual===4&&saturated.expectedMatches===2,"Congestion ceiling incorrect");
  return {status:"PASS",support:"Capacity/congestion induces mismatch between reciprocated intentions and exclusive matching; competent maximum matching beats naive greedy on exact graph",greedy_pairs:greedy,maximum_pairs:optimal,all_mutual_positive_edges:saturated.expectedMutual,all_mutual_formed_pairs:saturated.expectedMatches,next:"P05 separate formation flow from survivor stock"};
}

function runP05(){
  const formation=distribution([1,1,1,1]).expectedMatches;
  const h0=0,hl=.25,hh=.75;
  const stocks=[h0,hl,hh].map(h=>formation*(1-h));
  insist(formation===2 && Math.abs(stocks[1]-1.5)<1e-12&&Math.abs(stocks[2]-.5)<1e-12,"Hazard expectations wrong");
  insist(stocks[0]>=stocks[1]&&stocks[1]>=stocks[2],"Stock monotonicity failed");
  return {status:"PASS",support:"Fixed deterministic formation flow does not determine active stock without dissolution/survival",formed_pairs_flow:formation,expected_stocks_by_hazard:{h0:stocks[0],h025:stocks[1],h075:stocks[2]},next:"Return to AB-R STOP_R5; do not spend N93–N106 without independent legal data and ESBM-exclusive hypothesis"};
}

function runAll(){const tests=[runP01,runP02,runP03,runP04,runP05];return tests.map((f,i)=>({id:"P0"+(i+1),...f()}));}
if(typeof require!=="undefined" && typeof module!=="undefined" && require.main===module){console.log(JSON.stringify(runAll(),null,2));}
module.exports={maximumMatching,greedyMatching,distribution,worldQ,runP01,runP02,runP03,runP04,runP05,runAll};
