"use strict";
// N84 exploratory McMaster conditional randomization baseline, frozen before run.
// Maintains each dater's directed opportunities AND number of yes responses.
function n84Audit(csv) {
 function parse(l){let a=[],s="",q=false;for(let i=0;i<l.length;i++){let c=l[i];if(c==='"'){if(q&&l[i+1]==='"'){s+='"';i++}else q=!q}else if(c===','&&!q){a.push(s);s=""}else s+=c}a.push(s);return a}
 const lines=csv.trimEnd().split(/\r\n|\n/),cols=parse(lines.shift());
 for(let f of ["sub","partner","day","gender","meetAgain"])if(!cols.includes(f))throw Error("missing "+f);
 const ix=Object.fromEntries(cols.map((x,i)=>[x,i]));
 const rows=lines.map((line,i)=>{const v=parse(line);if(v.length!==cols.length)throw Error("wrong width"+i);return{actor:v[ix.sub],target:v[ix.partner],day:v[ix.day],sex:v[ix.gender],y:v[ix.meetAgain]};});
 const by=new Map(),groups=new Map(),yes=[];
 const key=r=>r.day+"\x1F"+r.actor+"\x1F"+r.target;
 for(let i=0;i<rows.length;i++){const r=rows[i];if(!["0","1"].includes(r.y))throw Error("invalid yes/no");yes.push(+r.y);let k=key(r);if(by.has(k))throw Error("duplicate");by.set(k,i);let id=r.day+"\x1F"+r.actor;if(!groups.has(id))groups.set(id,[]);groups.get(id).push(i);}
 const pairs=[],unpaired=[];
 for(let i=0;i<rows.length;i++){let r=rows[i],inverse=r.day+"\x1F"+r.target+"\x1F"+r.actor,j=by.get(inverse);if(j===undefined)unpaired.push(i);else if(i<j)pairs.push([i,j]);}
 if(rows.length!==719||pairs.length!==357||unpaired.length!==5||groups.size!==54)throw Error("precommitted source shape mismatch");
 const p=new Map(),yesTotals=new Map();
 for(let [actor,inds] of groups){let a=inds.reduce((s,i)=>s+yes[i],0);p.set(actor,a/inds.length);yesTotals.set(actor,a);}
 const expected=pairs.reduce((s,[i,j])=>s+p.get(rows[i].day+"\x1F"+rows[i].actor)*p.get(rows[j].day+"\x1F"+rows[j].actor),0);
 function mutual(values){let both=0;for(let [i,j] of pairs)if(values[i]===1&&values[j]===1)both++;return both;}
 const observed=mutual(yes);
 let x=0x1badd00d;function rand(){x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;}
 const reps=2000,ns=[],groupArr=[...groups.values()];
 for(let it=0;it<reps;it++){
  const vals=yes.slice();
  for(let ids of groupArr){
   const shuffle=ids.map(i=>yes[i]);
   for(let i=shuffle.length-1;i>0;i--){let j=Math.floor(rand()*(i+1)),tmp=shuffle[i];shuffle[i]=shuffle[j];shuffle[j]=tmp;}
   for(let k=0;k<ids.length;k++)vals[ids[k]]=shuffle[k];
  }
  for(let [a,inds] of groups){if(inds.reduce((s,i)=>s+vals[i],0)!==yesTotals.get(a))throw Error("actor marginal lost");}
  ns.push(mutual(vals));
 }
 ns.sort((a,b)=>a-b);
 const mean=ns.reduce((s,x)=>s+x,0)/reps,variance=ns.reduce((s,x)=>s+(x-mean)**2,0)/(reps-1),sd=Math.sqrt(variance);
 const tail=ns.filter(x=>Math.abs(x-expected)>=Math.abs(observed-expected)-1e-12).length;
 const result={status:"EXPLORATORY_PRIOR_OUTCOME_EXPOSURE",B:reps,seed_hex:"1badd00d",n_actors:54,n_sessions:2,n_directional:rows.length,n_complete_encounters:pairs.length,unmatched_directional:unpaired.length,observed_mutual:observed,expected_mutual_conditional_exact:expected,perm_mean:mean,perm_sd:sd,perm_quantiles:{q025:ns[Math.floor(reps*.025)],median:ns[Math.floor(reps*.5)],q975:ns[Math.floor(reps*.975)]},observed_minus_null_expected:observed-expected,randomization_two_sided_p_descriptive:(1+tail)/(reps+1),null_min:ns[0],null_max:ns[reps-1],qualifiers:"conditional permutation fixes each actor's number yes and all encounter arcs and session; participants reused, outcomes previously explored; descriptive exploratory not confirmatory causal test or external replication",invariants:{all_source_binary:true,complete_pairs_sum:true,each_actor_yes_preserved:true,perm_expected_consistent:Math.abs(mean-expected)<6*(sd/Math.sqrt(reps))}};
 if(!result.invariants.perm_expected_consistent)throw Error("analytic and Monte Carlo null disagree beyond 6 SE");
 return result;
}
