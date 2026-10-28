/* N46: Age-gap choices across Mixmosa original GitHub CSVs. Exports aggregate only.
   Pre-results prereg commit 6cabe7a8c007a6b3800aa84f0789a6e56489d1be.
*/
function csvParse(s){const lines=s.trimEnd().split(/\r?\n/);let header=lines.shift().split(',');return lines.map(line=>{const arr=[];let v='',q=false;for(let i=0;i<line.length;i++){let ch=line[i];if(ch==='"' && q && line[i+1]==='"'){v+='"';i++;}else if(ch==='"'){q=!q;}else if(ch===','&&!q){arr.push(v);v='';}else{v+=ch;}}arr.push(v);return Object.fromEntries(header.map((h,i)=>[h,arr[i]??'']));});}
const yes=x=>x==='true'||x==='1';
function rng32(seed){let a=seed>>>0;return ()=>{a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t^=t+Math.imul(t^(t>>>7),61|t);return ((t^(t>>>14))>>>0)/4294967296;};}
const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
function qtile(v,q){let a=v.slice().sort((x,y)=>x-y),z=(a.length-1)*q,i=Math.floor(z);return a[i]*(1-(z-i))+(a[Math.min(i+1,a.length-1)])*(z-i);}
function analysis(payload){const I=csvParse(payload.interactions),F=csvParse(payload.features),lookup=new Map(F.map(x=>[x.user_id,x]));let directed=[],missing=0;
 for(const d of I){const m=lookup.get(d.male_user_id),f=lookup.get(d.female_user_id);if(!m||!f||!m.age||!f.age||!Number.isFinite(+m.age)||!Number.isFinite(+f.age)||+m.age<16||+f.age<16||+m.age>90||+f.age>90){missing++;continue;}
 const ageM=+m.age,ageF=+f.age;directed.push({event:d.event_id,actor:d.male_user_id,sex:'men_choosing_women',gap:Math.abs(ageM-ageF),signed:ageF-ageM,dec:+yes(d.does_male_like_female)});
 directed.push({event:d.event_id,actor:d.female_user_id,sex:'women_choosing_men',gap:Math.abs(ageM-ageF),signed:ageM-ageF,dec:+yes(d.does_female_like_male)});
 }
 const rng=rng32(20261028);let output={source:'Mixmosa github csv/interactions + csv/user_features',dates: I.length,age_complete_dates:I.length-missing,age_missing_dates:missing,groups:{}};
 for(const sex of ['women_choosing_men','men_choosing_women']){
 const sub=directed.filter(x=>x.sex===sex);let g=new Map();sub.forEach((x,i)=>{let k=x.event+'|'+x.actor;if(!g.has(k))g.set(k,[]);g.get(k).push(i)});let categories={};
 for(const field of ['gap','signed']){let X=sub.map(x=>x[field]),Y=sub.map(x=>x.dec),obs=mean(X.filter((x,i)=>Y[i]===1))-mean(X),nulls=[];
 for(let b=0;b<1000;b++){let yy=Y.slice();for(const idx of g.values()){let val=idx.map(i=>Y[i]);for(let j=val.length-1;j>0;j--){let k=Math.floor(rng()*(j+1));[val[k],val[j]]=[val[j],val[k]];}idx.forEach((i,j)=>{yy[i]=val[j]});}nulls.push(mean(X.filter((x,i)=>yy[i]===1))-mean(X));}
 categories[field]={n_directed:sub.length,yes:Y.reduce((a,b)=>a+b,0),chooser_event_groups:g.size,groups_with_choice_variation:[...g.values()].filter(z=>z.some(i=>Y[i]===0)&&z.some(i=>Y[i]===1)).length,observed_diff:obs,null_mean:mean(nulls),null_p025:qtile(nulls,.025),null_p975:qtile(nulls,.975),p_lower:(1+nulls.filter(x=>x<=obs).length)/1001,p_upper:(1+nulls.filter(x=>x>=obs).length)/1001};
 }
 output.groups[sex]=categories;
 }
 return output;
}
