// Frozen original-data quality audit (noncycle); never print individual rows.
function auditSpeedDates(csv) {
  function parse(l) {
    const a=[]; let s="",q=false;
    for(let i=0;i<l.length;i++){
      const c=l[i];
      if(c==='"'){if(q&&l[i+1]==='"'){s+='"';i++;}else q=!q;}
      else if(c===','&&!q){a.push(s);s="";}else s+=c;
    }
    a.push(s);return a;
  }
  const lines=csv.trimEnd().split(/\r?\n/),h=parse(lines.shift());
  for(const f of ["sub","partner","day","gender","meetAgain"])
    if(!h.includes(f))throw Error("Missing column "+f);
  const ix=Object.fromEntries(h.map((x,i)=>[x,i]));
  const rows=lines.map((l,i)=>{
    const v=parse(l);if(v.length!==h.length)throw Error("Bad width "+i);
    return {id:v[ix.sub],partner:v[ix.partner],day:v[ix.day],
      gender:v[ix.gender],y:v[ix.meetAgain]};
  });
  const key=r=>[r.day,r.id,r.partner].join("\x1F");
  const reverse=r=>[r.day,r.partner,r.id].join("\x1F");
  const by=new Map();
  for(const r of rows){
    const k=key(r);if(!by.has(k))by.set(k,[]);
    by.get(k).push(r);
  }
  const duplicate=[...by.values()].filter(z=>z.length>1).length;
  const actor=new Set(rows.map(r=>r.id));
  const days=[...new Set(rows.map(r=>r.day))].sort();
  const sessionSummary=days.map((day,i)=>({
    ordinal:i+1,
    records:rows.filter(r=>r.day===day).length,
    actors:new Set(rows.filter(r=>r.day===day).map(r=>r.id)).size
  }));
  const binaryRows={yes:0,no:0,other:0};
  const byGender={M:{yes:0,no:0,other:0},F:{yes:0,no:0,other:0},other:{yes:0,no:0,other:0}};
  for(const r of rows){
    const bucket=r.y==="1"?"yes":r.y==="0"?"no":"other";
    binaryRows[bucket]++;
    byGender[r.gender in byGender?r.gender:"other"][bucket]++;
  }
  const pairs=[],unpaired=[];
  if(!duplicate)for(const r of rows){
    const mate=by.get(reverse(r));
    if(!mate)unpaired.push(r);
    else if(key(r)<reverse(r))pairs.push([r,mate[0]]);
  }
  const ct={neither:0,maleOnly:0,femaleOnly:0,mutual:0,invalid:0};
  for(const pair of pairs){
    const m=pair.find(r=>r.gender==="M"),f=pair.find(r=>r.gender==="F");
    if(!m||!f||!["0","1"].includes(m.y)||!["0","1"].includes(f.y)){
      ct.invalid++;continue;
    }
    if(m.y==="1"&&f.y==="1")ct.mutual++;
    else if(m.y==="1"&&f.y==="0")ct.maleOnly++;
    else if(m.y==="0"&&f.y==="1")ct.femaleOnly++;
    else ct.neither++;
  }
  const valid=pairs.length-ct.invalid;
  const pm=valid?(ct.maleOnly+ct.mutual)/valid:null;
  const pf=valid?(ct.femaleOnly+ct.mutual)/valid:null;
  const both=valid?ct.mutual/valid:null;
  return {status:"EXPLORATORY_NONCYCLE_AUDIT",noCausalClaim:true,
    rows:rows.length,fields:h.length,actors:actor.size,sessions:sessionSummary,
    directedKeys:by.size,duplicates:duplicate,matchedDates:pairs.length,
    unmatchedDirected:unpaired.length,binaryRows,byGender,
    dyads:ct,completeNativeBinaryDyads:valid,
    descriptiveRates:{maleYes:pm,femaleYes:pf,bothYes:both,
      independentMarginalsProduct:pm===null?null:pm*pf,
      mutualMinusProduct:both===null?null:both-pm*pf}};
}
