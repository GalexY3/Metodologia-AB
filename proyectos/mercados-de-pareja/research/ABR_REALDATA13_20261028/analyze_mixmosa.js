/* ABR-REALDATA13-20261028 · aggregate-only analysis of Mixmosa source.
 * Source pinned by Git blob SHA in PREREG.json; no raw participant output.
 * Exploratory study: in-person 8-minute dates, NOT Tinder, not Spain.
 */
function parseCsv(s) {
  const lines=s.trimEnd().split(/\r?\n/), h=lines.shift().split(",");
  return lines.map(line=>{
    let a=[],v="",q=false;
    for(let i=0;i<line.length;i++){
      const c=line[i];
      if(c==='"' && q && line[i+1]==='"'){v+='"';i++;}
      else if(c==='"'){q=!q;}
      else if(c===',' && !q){a.push(v);v="";}
      else v+=c;
    }
    a.push(v); return Object.fromEntries(h.map((k,j)=>[k,a[j]??""]));
  });
}
const truth=x=>x==="true"||x==="1";
function mean(v){return v.reduce((a,b)=>a+b,0)/v.length;}
function corr(xs,ys){
  if(xs.length<4)return null;
  const mx=mean(xs),my=mean(ys);
  let xx=0,yy=0,xy=0;
  for(let i=0;i<xs.length;i++){const a=xs[i]-mx,b=ys[i]-my;xx+=a*a;yy+=b*b;xy+=a*b;}
  return xx>0&&yy>0?xy/Math.sqrt(xx*yy):null;
}
function rng32(seed){
  let a=seed>>>0;return ()=>{
    a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);
    t^=t+Math.imul(t^(t>>>7),61|t);
    return ((t^(t>>>14))>>>0)/4294967296;
  };
}
function shuffled(vals,rng){
  let a=vals.slice();for(let i=a.length-1;i>0;i--){let j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;
}
const uniq=a=>new Set(a).size;
function rateByQuantile(data){
  // Date-weighted quartiles: duplicate profile exposures are intentional.
  const sorted=data.map(x=>x.x).sort((a,b)=>a-b);
  if(sorted.length<60)return {n:sorted.length,gate:"INSUFFICIENT"};
  const cut=[.25,.5,.75].map(q=>sorted[Math.floor(q*(sorted.length-1))]);
  const g=Array.from({length:4},()=>[]);
  for(const p of data){let j=cut.findIndex(v=>p.x<=v);g[j<0?3:j].push(p.y);}
  return {n:data.length,cutpoints:cut,quartiles:g.map(a=>({n:a.length,like_rate:a.length?mean(a):null}))};
}
function centeredAssociation(data){
  const grp=Object.groupBy(data,x=>x.event);
  let xy=0,xx=0,yy=0;
  for(const rows of Object.values(grp)){
    const ax=mean(rows.map(x=>x.x)),ay=mean(rows.map(x=>x.y));
    for(const r of rows){let a=r.x-ax,b=r.y-ay;xy+=a*b;xx+=a*a;yy+=b*b;}
  }
  return xx&&yy?xy/Math.sqrt(xx*yy):null;
}
function runMixmosa(payload){
  const D=parseCsv(payload.interactions),F=parseCsv(payload.features),S=parseCsv(payload.swipes),E=parseCsv(payload.events);
  const feature=new Map(F.map(x=>[x.user_id,x]));
  const events=Object.groupBy(D,x=>x.event_id);
  const byFemaleEvent=Object.groupBy(D,(x)=>x.event_id+"|"+x.female_user_id);
  const sw=new Map(S.map(x=>[[x.event_id,x.swiper_user_id,x.swipee_user_id].join("|"),truth(x.liked)]));
  let dups=0,seen=new Set(),badJoint=0,swMissing=0,swConflict=0,bothFeat=0;
  const stats={male_like:0,female_like:0,mutual:0};
  const photoMale=[],photoFemale=[],incMale=[],incFemale=[],agePairs=[];
  const receivedMale=new Map(),receivedFemale=new Map();
  const incRanks=new Map(Array.from({length:9},(_,i)=>[String(i+1),i+1])); // Derived CSV encodes 1..9, not raw bracket strings.
  for(const r of D){
    const key=[r.event_id,r.male_user_id,r.female_user_id].join("|");
    if(seen.has(key))dups++;seen.add(key);
    const m=truth(r.does_male_like_female),f=truth(r.does_female_like_male);
    stats.male_like+=+m;stats.female_like+=+f;stats.mutual+=+(m&&f);
    badJoint+=+((m&&f)!==truth(r.mutual_interest));
    const sm=sw.get([r.event_id,r.male_user_id,r.female_user_id].join("|"));
    const sf=sw.get([r.event_id,r.female_user_id,r.male_user_id].join("|"));
    swMissing+=(sm===undefined?1:0)+(sf===undefined?1:0);
    swConflict+=(sm!==undefined&&sm!==m?1:0)+(sf!==undefined&&sf!==f?1:0);
    const fm=feature.get(r.male_user_id),fw=feature.get(r.female_user_id);
    if(fm&&fw)bothFeat++;
    if(fm){let n=Number(fm.avg_physical_attractiveness_rating);if(fm.avg_physical_attractiveness_rating!==""&&Number.isFinite(n))photoMale.push({event:r.event_id,x:n,y:+f});
      let v=incRanks.get(fm.income_bucket);if(v)incMale.push({event:r.event_id,x:v,y:+f});
    }
    if(fw){let n=Number(fw.avg_physical_attractiveness_rating);if(fw.avg_physical_attractiveness_rating!==""&&Number.isFinite(n))photoFemale.push({event:r.event_id,x:n,y:+m});
      let v=incRanks.get(fw.income_bucket);if(v)incFemale.push({event:r.event_id,x:v,y:+m});
    }
    if(fm&&fw&&fm.age&&fw.age)agePairs.push({event:r.event_id,x:Math.abs(Number(fm.age)-Number(fw.age)),y:+(m&&f)});
    const a=receivedMale.get(r.male_user_id)||{n:0,yes:0};a.n++;a.yes+=+f;receivedMale.set(r.male_user_id,a);
    const b=receivedFemale.get(r.female_user_id)||{n:0,yes:0};b.n++;b.yes+=+m;receivedFemale.set(r.female_user_id,b);
  }
  let sexIdsM=uniq(D.map(x=>x.male_user_id)),sexIdsF=uniq(D.map(x=>x.female_user_id));
  const p={interactions:D.length,users_features:F.length,swipes:S.length,events_in_dataset:E.length,events_in_interactions:Object.keys(events).length,unique_male:sexIdsM,unique_female:sexIdsF,duplicate_event_dyads:dups,flags_mismatched:badJoint,interactions_both_features:bothFeat,swipe_direction_missing:swMissing,swipe_decision_conflicts:swConflict};
  if(dups||badJoint)throw Error("Invalid data grain or mutual outcome");
  const B=1000,rng=rng32(20261028);
  let nullEvent=[],nullFemale=[];
  for(let k=0;k<B;k++){
    let total=0,other=0;
    for(const rows of Object.values(events)){
      const m=rows.map(x=>+truth(x.does_male_like_female)),f=shuffled(rows.map(x=>+truth(x.does_female_like_male)),rng);
      for(let i=0;i<m.length;i++)total+=m[i]*f[i];
    }
    for(const rows of Object.values(byFemaleEvent)){
      const m=rows.map(x=>+truth(x.does_male_like_female)),f=shuffled(rows.map(x=>+truth(x.does_female_like_male)),rng);
      for(let i=0;i<m.length;i++)other+=m[i]*f[i];
    }
    nullEvent.push(total);nullFemale.push(other);
  }
  const nul=x=>({mean:mean(x),min:Math.min(...x),max:Math.max(...x),q025:x.slice().sort((a,b)=>a-b)[Math.floor(.025*B)],q975:x.slice().sort((a,b)=>a-b)[Math.floor(.975*B)],p_upper:(1+x.filter(v=>v>=stats.mutual).length)/(B+1),p_lower:(1+x.filter(v=>v<=stats.mutual).length)/(B+1)});
  const byEvent=Object.entries(events).map(([event,rows])=>{let m=rows.filter(x=>truth(x.does_male_like_female)).length,w=rows.filter(x=>truth(x.does_female_like_male)).length,mutual=rows.filter(x=>truth(x.mutual_interest)).length;return {event,n:rows.length,male_like:m,female_like:w,mutual,independence_expectation:m*w/rows.length};});
  // LOO receiver popularity: exclude the focal date itself; threshold >=3 other dates.
  const loo=[];
  for(const d of D){
    const m=receivedMale.get(d.male_user_id),w=receivedFemale.get(d.female_user_id);
    if(m.n-1<3||w.n-1<3)continue;
    const mm=(m.yes-Number(truth(d.does_female_like_male)))/(m.n-1),ww=(w.yes-Number(truth(d.does_male_like_female)))/(w.n-1);
    loo.push({event:d.event_id,x:mm,y:ww,mutual:truth(d.mutual_interest)});
  }
  const matched=loo.filter(x=>x.mutual);
  const countEvent=(arr)=>Object.keys(Object.groupBy(arr,x=>x.event)).length;
  return {provenance:{source:"dankras/mixmosa-anonymized-data",file_grain:"in-person 8-minute date",date_records_actual:D.length,repository_readme_claim:2961},quality:p,outcomes:{...stats,male_like_rate:stats.male_like/D.length,female_like_rate:stats.female_like/D.length,mutual_rate:stats.mutual/D.length,events:byEvent.length},permutation:{reps:B,observed_mutual:stats.mutual,eventwise:nul(nullEvent),female_eventwise:nul(nullFemale),event_independent_expectation:byEvent.reduce((s,v)=>s+v.independence_expectation,0)},features:{male_candidate_photo:{...rateByQuantile(photoMale),r:corr(photoMale.map(x=>x.x),photoMale.map(x=>x.y)),r_within_event:centeredAssociation(photoMale)},female_candidate_photo:{...rateByQuantile(photoFemale),r:corr(photoFemale.map(x=>x.x),photoFemale.map(x=>x.y)),r_within_event:centeredAssociation(photoFemale)},male_candidate_income:{...rateByQuantile(incMale),r:corr(incMale.map(x=>x.x),incMale.map(x=>x.y)),r_within_event:centeredAssociation(incMale)},female_candidate_income:{...rateByQuantile(incFemale),r:corr(incFemale.map(x=>x.x),incFemale.map(x=>x.y)),r_within_event:centeredAssociation(incFemale)},age_gap:{n:agePairs.length,mean:mean(agePairs.map(x=>x.x)),r_with_mutual:corr(agePairs.map(x=>x.x),agePairs.map(x=>x.y)),r_within_event:centeredAssociation(agePairs),quartiles:rateByQuantile(agePairs).quartiles}},popularity_leave_one_out:{eligible_edges:loo.length,eligible_mutual:matched.length,eligible_events:countEvent(loo),mutual_events:countEvent(matched),r_all_dates:corr(loo.map(x=>x.x),loo.map(x=>x.y)),r_mutual_only:corr(matched.map(x=>x.x),matched.map(x=>x.y)),GATE_PASS:matched.length>=60&&countEvent(matched)>=5},audit_notes:["eventwise permute female acceptance across dates in each event; preserves event yes marginals, not individual's choice preferences","female_eventwise permute each woman's choices within event; preserves each woman's yes frequency and event, not available candidate attributes","photo and income associations are event-weighted descriptive only, never causal","leave-one-out popularity is fitted using other observed dates; could share event selection, not independent test set"]};
}
