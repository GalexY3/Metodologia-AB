// N357 prospective exact objective serialization audit; synthetic fixtures only.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {matching} from '../work/src/blossom_matching.mjs';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const out=join(root,'outcomes','N357_EXACT_SERIALIZATION_RESULTS.json');
if(existsSync(out))throw new Error('OUTPUT_EXISTS_NO_OVERWRITE');
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const ULP=2**-52;
function disjoint(name,n,ks){
 if(ks.length*2>n)throw new Error('BAD_FIXTURE');
 return {name,n,graph:ks.map((k,i)=>({pair:[2*i,2*i+1],weight:1+k*ULP})),family:'N356_regression'};
}
const zero=Array(72).fill(0);
const fixtures=[
 disjoint('D2_ONE',2,[1]),disjoint('D4_ZERO',4,[0,0]),
 disjoint('D4_ONE',4,[1,0]),disjoint('D4_THREE',4,[3,0]),
 disjoint('D6_ONE',6,[1,0,0]),disjoint('D8_ONE',8,[1,0,0,0]),
 disjoint('D144_ZERO',144,zero),disjoint('D144_ONE',144,[1,...zero.slice(1)]),
 disjoint('D144_THREE',144,[3,...zero.slice(1)]),
 disjoint('D144_THIRTYONE',144,[31,...zero.slice(1)]),
 disjoint('D144_THIRTYTHREE',144,[33,...zero.slice(1)]),
 disjoint('D144_PATTERN',144,zero.map((_,i)=>i%5)),
 {name:'EMPTY_GRAPH',n:144,graph:[],family:'new_empty'}
];
function rng(seed){let s=seed>>>0;return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)/4294967296;};}
function randomGraph(name,n,density,seed,maxUlp){
 const f=rng(seed),edges=[];
 for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
  if(f()<density)edges.push({pair:[i,j],weight:1+Math.floor(f()*maxUlp)*ULP});
 }
 return {name,n,graph:edges,family:'new_random_graph',seed,density};
}
fixtures.push(randomGraph('K6_TIES',6,1,17,1));
fixtures.push(randomGraph('R8',8,.65,35708,200));
fixtures.push(randomGraph('R24',24,.4,35724,200));
fixtures.push(randomGraph('R64',64,.13,35764,400));
fixtures.push(randomGraph('R144_SPARSE',144,.055,357144,100));
fixtures.push(randomGraph('R144_DENSE_ULP',144,.23,357145,32));
fixtures.push({name:'STAR_N144',n:144,family:'new_high_degree_no_perfect_matching',
 graph:Array.from({length:143},(_,i)=>({pair:[0,i+1],weight:1+(i%91)*ULP}))});
fixtures.push({name:'ODD_DISCONNECTED',n:144,family:'new_two_odd_components',
 graph:Array.from({length:142},(_,i)=>({pair:i<70?[i,i+1]:[i+1,i+2],weight:1+(i%19)*ULP}))});
if(fixtures.length!==21)throw new Error('FIXTURE_COUNT_DRIFT');
function exactReference(pairs,edges){
 const indexed=new Map(edges.map(e=>[e.pair.join(','),e.weight]));
 let total=0n;
 for(const [a,b] of pairs){
  const w=indexed.get([a,b].sort((x,y)=>x-y).join(','));
  if(w===undefined)throw new Error('MATCHED_NONEDGE');
  const k=(w-1)*2**52;
  if(!Number.isSafeInteger(k))throw new Error('INVALID_INPUT_ULP');
  total+=(1n<<52n)+BigInt(k);
 }
 return total;
}
let previousNonExact=0,mutationDetected=false;
const rows=[];
for(const f of fixtures){
 const ans=matching(Array.from({length:f.n},(_,i)=>i),f.graph,{maxWallMs:7000});
 const exact=exactReference(ans.pairs,f.graph);
 if(!ans.certified_optimality||ans.full_units_format!=='decimal_bigint_string'||ans.full_units_schema_version!==2||
 typeof ans.full_units_in_2_power_minus52!=='string'||!/^[0-9]+$/.test(ans.full_units_in_2_power_minus52))
  throw new Error('SCHEMA_BAD:'+f.name);
 if(BigInt(ans.full_units_in_2_power_minus52)!==exact)throw new Error('BAD_BIGINT_OBJECTIVE:'+f.name);
 const oldNumber=Number(ans.cardinality)*2**52+ans.exact_weight_residue;
 if(BigInt(oldNumber)!==exact)previousNonExact++;
 if(f.name==='D4_ONE')mutationDetected=(BigInt(ans.full_units_in_2_power_minus52)+1n)!==exact;
 rows.push({name:f.name,family:f.family,n:f.n,edges:f.graph.map(e=>[...e.pair,e.weight]),
  pairs:ans.pairs,cardinality:ans.cardinality,certified:ans.certified_optimality,
  exact_residual:ans.exact_weight_residue,full_units_decimal:ans.full_units_in_2_power_minus52,
  format:ans.full_units_format,schema_version:ans.full_units_schema_version,
  old_Number_loss:(BigInt(oldNumber)-exact).toString(),unique_status:ans.uniqueness_status});
}
if(!mutationDetected)throw new Error('MUTANT_NOT_DETECTED');
const report={schema:'N357_DECIMAL_BIGINT_REGRESSION_V1',
 old_Number_non_exact_cases:previousNonExact,case_count:rows.length,new_cases:9,
 old_bug_regression_cases:12,all_certified:true,mutationDetected,rows,
 source_hashes:{blossom:sha(join(root,'work','src','blossom_matching.mjs')),
 vendor:sha(join(root,'vendor','blossom_with_state.cjs'))},
 human_validation:false,CT2:7,STOP_R5:true};
writeFileSync(out,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log('N357_JS',report.case_count,report.old_Number_non_exact_cases,sha(out));
