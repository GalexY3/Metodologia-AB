// AB-H N356 prospective audit: full_units output numerical integrity.
// Only new small disjoint-edge fixtures; never reruns historical simulations.
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {matching} from '../work/src/blossom_matching.mjs';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const output=join(root,'outcomes','N356_NUMERIC_PRECISION_BOUNDARY.json');
if(existsSync(output)) throw new Error('REFUSE_OVERWRITE_PREEXISTING_OUTCOME');
const ULPSCALE=2n**52n;
const hash=f=>createHash('sha256').update(readFileSync(f)).digest('hex');
function make(name, n, ks){
  if (ks.length*2>n) throw new Error('INVALID_N');
  return {name,n,graph:ks.map((k,i)=>{
    if(!Number.isSafeInteger(k)||k<0||k>127)throw new Error('INVALID_K');
    return {pair:[i*2,i*2+1], weight:1+k*2**-52};
  })};
}
const zero72=Array(72).fill(0);
const controls=[
  make('POS_SINGLE_ONE_ULP',2,[1]),
  make('POS_DOUBLE_ZERO_ULP',4,[0,0]),
  make('NEG_DOUBLE_ONE_ULP',4,[1,0]),
  make('NEG_DOUBLE_THREE_ULP',4,[3,0]),
  make('NEG_TRIPLE_ONE_ULP',6,[1,0,0]),
  make('NEG_QUAD_ONE_ULP',8,[1,0,0,0]),
  make('POS_N144_ALL_INTEGER',144,zero72),
  make('NEG_N144_ONE_ULP',144,[1,...zero72.slice(1)]),
  make('NEG_N144_THREE_ULP',144,[3,...zero72.slice(1)]),
  make('NEG_N144_31_ULP',144,[31,...zero72.slice(1)]),
  make('NEG_N144_33_ULP',144,[33,...zero72.slice(1)]),
  make('MIX_N144_PATTERN',144,zero72.map((_,i)=>i%5))
];
const rows=[];
for (const fixture of controls){
  const t0=performance.now();
  const answer=matching(Array.from({length:fixture.n},(_,i)=>i),fixture.graph,{maxWallMs:3000});
  if(!answer.certified_optimality)throw new Error('MATCHING_NOT_CERTIFIED');
  const actualFromReportedFields=BigInt(answer.cardinality)*ULPSCALE+BigInt(answer.exact_weight_residue);
  const published=BigInt(answer.full_units_in_2_power_minus52);
  const err=published-actualFromReportedFields;
  if(answer.cardinality!==fixture.graph.length)throw new Error('EXPECTED_DISJOINT_MATCHING_MISSING');
  rows.push({name:fixture.name,n:fixture.n,k_list:fixture.graph.map(e=>(e.weight-1)*2**52),
    pairs:answer.pairs,cardinality:answer.cardinality,
    certified_optimality:answer.certified_optimality,
    exact_weight_residue:answer.exact_weight_residue,
    published_full_units:answer.full_units_in_2_power_minus52,
    published_is_safe: Number.isSafeInteger(answer.full_units_in_2_power_minus52),
    big_integer_full_units:actualFromReportedFields.toString(),
    published_minus_true_big_integer_units:err.toString(),
    mismatch:err!==0n, elapsed_ms:Math.round((performance.now()-t0)*1000)/1000});
}
const result={
  schema:'ABH_N356_INTEGER_EXACTNESS_OF_SERIALIZED_OBJECTIVE_V1',
  caveat:'Software representation audit only; not new social evidence or new matching optimality validation',
  source_sha256:{
    blossom_matching:hash(join(root,'work','src','blossom_matching.mjs')),
    blossom_vendor:hash(join(root,'vendor','blossom_with_state.cjs'))
  },
  controls:rows.length,reporting_mismatches:rows.filter(r=>r.mismatch).length,
  reported_safe:rows.filter(r=>r.published_is_safe).length,
  rows,CT2_scientific:7,STOP_R5_human:true};
writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log('N356_RESULT',JSON.stringify({controls:result.controls,
  reporting_mismatches:result.reporting_mismatches,reported_safe:result.reported_safe,
  sha256:hash(output)}));
