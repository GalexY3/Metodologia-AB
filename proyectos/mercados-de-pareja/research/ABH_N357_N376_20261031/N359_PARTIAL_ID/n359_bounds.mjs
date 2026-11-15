// AB-H N359: prospective partial-identification experiment, synthetic only.
import { writeFileSync, readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const output=join(root,'outcomes','N359_PARTIAL_ID_SYNTHETIC.json');
if(existsSync(output))throw Error('NO_OVERWRITE');
const N=9, RATES=[0.15,0.35,0.60,0.85], MODES=['MCAR','ACTOR_SELECT','OUTCOME_MNAR'];
function random(seed){let s=seed>>>0;return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)/4294967296;};}
function match(edges,n){ // augmenting-path maximum bipartite-cardinality matching
 const partner=Array(n).fill(-1);
 function augment(i,seen){
  for(let j=0;j<n;j++)if(edges[i*n+j]&&!seen[j]){
   seen[j]=true;
   if(partner[j]===-1||augment(partner[j],seen)){partner[j]=i;return true;}
  }
  return false;
 }
 let count=0;
 for(let i=0;i<n;i++)if(augment(i,Array(n).fill(false)))count++;
 return count;
}
function generate(seed,mode,rate){
 const rng=random(seed),act=Array.from({length:N},()=>rng()),
  targetF=Array.from({length:N},()=>rng()),targetM=Array.from({length:N},()=>rng());
 const observed=[],f=[],m=[];
 for(let i=0;i<N;i++)for(let j=0;j<N;j++){
  const affinity=rng();
  const logitF=-0.50+1.3*(targetM[j]-0.5)+1.0*(affinity-0.5);
  const logitM=-0.50+1.3*(targetF[i]-0.5)+1.0*(affinity-0.5);
  const vf=Number(rng() < 1/(1+Math.exp(-logitF)));
  const vm=Number(rng() < 1/(1+Math.exp(-logitM)));
  let p=rate;
  if(mode==='ACTOR_SELECT')p=rate*(0.30+1.40*act[i]);
  if(mode==='OUTCOME_MNAR')p=rate*(vf&&vm?1.40:0.55);
  p=Math.max(0.01,Math.min(0.99,p));
  const visible=rate===1?1:Number(rng()<p);
  f.push(vf);m.push(vm);observed.push(visible);
 }
 const actual=f.map((v,i)=>Number(v&&m[i]));
 const lower=actual.map((v,i)=>Number(v&&observed[i]));
 const upper=actual.map((v,i)=>Number(v||!observed[i]));
 const L=match(lower,N),U=match(upper,N),K=match(actual,N);
 if(!(0<=L&&L<=K&&K<=U&&U<=N))throw Error('INVALID_IDENTIFICATION_SET');
 if(rate===1&&!(L===U&&U===K))throw Error('FULL_OBS_CONTRADICTION');
 return {seed,mode,rate,n:N,observed,f_choice:f,m_choice:m,L,U,K,width:U-L,
  observed_pairs:observed.reduce((a,v)=>a+v,0),
  observed_mutual:lower.reduce((a,v)=>a+v,0)};
}
const rows=[];
for(let modeIndex=0;modeIndex<MODES.length;modeIndex++){
 const mode=MODES[modeIndex];
 for(let rateIndex=0;rateIndex<RATES.length;rateIndex++){
  const rate=RATES[rateIndex];
  for(let repetition=0;repetition<40;repetition++){
   const seed=359000+modeIndex*10000+rateIndex*1000+repetition;
   rows.push(generate(seed,mode,rate));
  }
 }
 for(let rep=0;rep<8;rep++)rows.push(generate(459000+modeIndex*100+rep,mode,1));
}
if(rows.length!==504)throw Error('WRONG_UNIT_COUNT');
const a=[];
for(const mode of MODES)for(const rate of [...RATES,1]){
 const x=rows.filter(z=>z.mode===mode&&z.rate===rate);
 a.push({mode,rate,n:x.length,meanWidth:x.reduce((sum,r)=>sum+r.width,0)/x.length,
  pointIdentified:x.filter(z=>z.L===z.U).length,
  meanObserved:x.reduce((sum,r)=>sum+r.observed_pairs,0)/x.length});
}
const manual={n:4,
 observed:[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1],
 female_choices:[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
 male_choices:[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]};
const low=manual.observed.map(()=>0);
const high=manual.observed.map(v=>Number(!v));
const manualL=match(low,4),manualU=match(high,4);
if(manualL!==0||manualU!==4)throw Error('OBSERVATIONAL_EQUIVALENCE_CONTROL_FAILED');
const digest=f=>createHash('sha256').update(readFileSync(f)).digest('hex');
const out={schema:'ABH_N359_SHARP_IDENTIFICATION_BOUNDS_V1',
 experiment:'Only synthetic bilateral choices on prespecified n=9+n=9 markets. Not inference about humans.',
 ab_cycle:'N359',single_cycle:true,
 estimator:'Maximum cardinality matching of mutually accepting pairs',
 rows,aggregates:a,
 manual_counterexample:{...manual,completion_zero_matching:manualL,completion_all_hidden_yes_matching:manualU,
  same_observed_records:true},
 assertions:{all_lower_le_true_le_upper:true,full_observation_collapses:true,
  tight_endpoints_constructive:true},
 source_js_sha256:digest(join(root,'instrument','n359_bounds.mjs')),
 human_validation:false,CT2:7,STOP_R5:true};
writeFileSync(output,JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log('N359_JS',rows.length,a.map(x=>x.mode+':'+x.rate+'='+x.meanWidth.toFixed(3)).join(' '),
 digest(output));
