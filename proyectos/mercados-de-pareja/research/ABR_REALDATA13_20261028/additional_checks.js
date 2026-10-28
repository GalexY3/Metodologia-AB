/* N33 N34 N35 supplementary aggregate-only analysis; exploratory.
   Pinned source: Mixmosa GitHub original blobs as in PREREG.
   Uses observed 8-minute interactions, not relationship formations.
*/
function parseCSV(s){let ls=s.trimEnd().split(/\r?\n/),hdr=ls.shift().split(",");return ls.map(l=>{let a=[],v="",q=false;for(let i=0;i<l.length;i++){let c=l[i];if(c==='"'&&q&&l[i+1]==='"'){v+='"';i++;}else if(c==='"')q=!q;else if(c===','&&!q){a.push(v);v="";}else v+=c;}a.push(v);return Object.fromEntries(hdr.map((x,i)=>[x,a[i]??""]))});}
const T=x=>x==="true"||x==="1";
function corr(x,y){if(x.length<4)return null;let mx=x.reduce((a,b)=>a+b,0)/x.length,my=y.reduce((a,b)=>a+b,0)/y.length,xx=0,yy=0,xy=0;for(let i=0;i<x.length;i++){let a=x[i]-mx,b=y[i]-my;xx+=a*a;yy+=b*b;xy+=a*b;}return xx*yy>0?xy/Math.sqrt(xx*yy):null}
function gen(seed){let a=seed>>>0;return()=>{a=(a+0x6d2b79f5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t^=t+Math.imul(t^(t>>>7),61|t);return ((t^(t>>>14))>>>0)/4294967296;}}
function shuffle(a,r){a=a.slice();for(let i=a.length-1;i>0;i--){let j=Math.floor(r()*(i+1));[a[j],a[i]]=[a[i],a[j]]}return a;}
function rate(events){const r=[];for(const rows of Object.values(events)){const n=rows.length,m=rows.filter(x=>x.m).length,f=rows.filter(x=>x.f).length,o=rows.filter(x=>x.b).length;r.push({n,m,f,o,exp:m*f/n});}return r;}
function run(p){
  const I=parseCSV(p.interactions),S=parseCSV(p.swipes),F=parseCSV(p.features),features=new Map(F.map(x=>[x.user_id,x]));
  const seen=new Set(),countM=new Map(),countF=new Map(),eventParticipants=new Map(),eventRows=new Map(),edges=[];
  for(const a of I){
    const b={ev:a.event_id,mID:a.male_user_id,fID:a.female_user_id,m:T(a.does_male_like_female),f:T(a.does_female_like_male),b:T(a.mutual_interest)};
    if(!eventRows.has(b.ev))eventRows.set(b.ev,[]);eventRows.get(b.ev).push(b);
    if(!eventParticipants.has(b.ev))eventParticipants.set(b.ev,new Set());eventParticipants.get(b.ev).add(b.mID);eventParticipants.get(b.ev).add(b.fID);
    edges.push(b);
    let cm=countM.get(b.mID)||{n:0,yes:0};cm.n++;cm.yes+=+b.f;countM.set(b.mID,cm);
    let cf=countF.get(b.fID)||{n:0,yes:0};cf.n++;cf.yes+=+b.m;countF.set(b.fID,cf);
  }
  const scored=[];
  for(const e of edges){const m=countM.get(e.mID),f=countF.get(e.fID);
    if(m.n<4||f.n<4)continue;
    const va=(m.yes-Number(e.f))/(m.n-1),vb=(f.yes-Number(e.m))/(f.n-1);
    scored.push({ev:e.ev,x:va,y:vb,b:e.b});}
  const both=scored.filter(x=>x.b),events=Object.groupBy(scored,x=>x.ev),B=1000,rng=gen(20261028);
  const sim=[];
  for(let z=0;z<B;z++){
    let xs=[],ys=[];
    for(const rows of Object.values(events)){
      const flags=shuffle(rows.map(x=>x.b),rng);
      for(let i=0;i<rows.length;i++)if(flags[i]){xs.push(rows[i].x);ys.push(rows[i].y);}
    }
    sim.push(corr(xs,ys));
  }
  const valid=sim.filter(x=>x!==null),ordered=valid.slice().sort((a,b)=>a-b),obs=corr(both.map(x=>x.x),both.map(x=>x.y));
  let realEventRates=rate(Object.fromEntries(eventRows));
  const differences=realEventRates.map(x=>x.o-x.exp),totalDiff=differences.reduce((a,b)=>a+b,0);
  let avg=realEventRates.reduce((a,b)=>a+b.n,0);
  const leaveOneOut=realEventRates.map((x,i)=>({removed_event_index:i,observed_minus_expected_per_date:(totalDiff-differences[i])/(avg-x.n)}));
  // Read swipes only as aggregates. The extra records are other decisions not qualifying as a complete date.
  const dateDirectional=new Set(edges.flatMap(x=>[[x.ev,x.mID,x.fID].join("|"),[x.ev,x.fID,x.mID].join("|")]));
  let extra=0;for(const s of S)if(!dateDirectional.has([s.event_id,s.swiper_user_id,s.swipee_user_id].join("|")))extra++;
  const userEvents=new Map();for(const [id,ids] of eventParticipants){for(const person of ids){if(!userEvents.has(person))userEvents.set(person,new Set());userEvents.get(person).add(id);}}
  return {N33:{eligible_dates:scored.length,mutual_dates:both.length,events_with_both_measured:Object.keys(events).length,observed_popularity_correlation:obs,all_date_popularity_correlation:corr(scored.map(x=>x.x),scored.map(x=>x.y)),null_permutation_reps:valid.length,perm_mean:valid.reduce((a,b)=>a+b,0)/valid.length,perm_q025:ordered[Math.floor(.025*valid.length)],perm_q975:ordered[Math.floor(.975*valid.length)],perm_lower_p:(1+valid.filter(x=>x<=obs).length)/(valid.length+1),perm_upper_p:(1+valid.filter(x=>x>=obs).length)/(valid.length+1),warning:"LOO scores use other dates from same event; conditional on observed exposure; event matching shuffle does not preserve individual yes-degree."},N34:{interaction_dates:edges.length,observed_directional_swipes:S.length,expected_directional_date_records:edges.length*2,extra_swipes_not_part_of_interactions:extra,unknown_interaction_origins:"The additional swipes may not reflect complete paired dates; no assertions about scope",distinct_users_across_dates:userEvents.size},N35:{events:realEventRates.length,overall_event_conditional_mutual_excess:totalDiff,per_date_excess:totalDiff/avg,leave_one_event_out_excess_range:[Math.min(...leaveOneOut.map(x=>x.observed_minus_expected_per_date)),Math.max(...leaveOneOut.map(x=>x.observed_minus_expected_per_date))],participant_events:{one_event:[...userEvents.values()].filter(x=>x.size===1).length,multiple_events:[...userEvents.values()].filter(x=>x.size>1).length,max_events:Math.max(...[...userEvents.values()].map(x=>x.size))},warnings:["Observed date edges not random sample of all eligible people, event-wise shuffling is not a randomization experiment","Repeated users create cross-event dependence; event-level bootstrap CI not robust alone"]}};
}
