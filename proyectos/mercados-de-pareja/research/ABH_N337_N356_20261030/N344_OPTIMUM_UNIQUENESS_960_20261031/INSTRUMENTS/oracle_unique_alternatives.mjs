// N344 independent uniqueness diagnostic by forbidding each chosen edge.
// A matching differs iff it omits at least one edge of the chosen matching;
// exhaustive re-optimization of every forbidden selected edge gives a proof
// of uniqueness when all alternative objectives are strictly inferior.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {matching} from '../work/src/blossom_matching.mjs';
import {readFloat64LE} from '../work/src/io.ts';
import {createHash} from 'node:crypto';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const nidx=JSON.parse(readFileSync(join(root,'outcomes','N342_NATIVE_INDEX.json'),'utf8'));
const tidx=JSON.parse(readFileSync(join(root,'outcomes','N341_TS60_INDEX.json'),'utf8'));
const input=JSON.parse(readFileSync(join(root,'N341_INPUT_MANIFEST.json'),'utf8'));
const output=join(root,'outcomes','N344_UNIQUENESS.json');
if(existsSync(output))throw new Error('NO_OUTPUT_OVERWRITE');
if(nidx.rows.length!==60||tidx.rows.length!==60||input.rows.length!==6)throw new Error('FROZEN_DATASET_SHAPE_CHANGED');
const nodes=Array.from({length:144},(_,i)=>i);
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const results=[];
for(const seedrow of input.rows){
  const seed=seedrow.seed, data=seedrow.tensors.u_match;
  const tpath=join(root,'official_inputs_60',data.path);
  if(sha(tpath)!==data.sha256)throw new Error(`N344_TENSOR_SHA_CHANGED:${seed}`);
  const tensor=readFloat64LE(tpath,data.sha256,data.shape);
  for(let k=0;k<10;k++){
    const p=nidx.rows.find(x=>x.seed===seed&&x.scenario===input.scenario_order[k]);
    const j=tidx.rows.find(x=>x.seed===seed&&x.scenario===input.scenario_order[k]);
    if(!p||!j)throw new Error('MISSING_SEED_SCENARIO');
    const pytrace=join(root,'outcomes',p.trace_path),tsout=join(root,'outcomes',j.run_file);
    if(sha(pytrace)!==p.trace_sha256||sha(tsout)!==j.run_sha256)throw new Error('DATA_SHA_CHANGED');
    const positive=Array.from({length:16},()=>new Map());
    for(const line of readFileSync(pytrace,'utf8').trimEnd().split('\n')){
      const e=JSON.parse(line);
      if(e.stage!=='response'||!e.decision)continue;
      const a=Math.min(e.i,e.j),b=Math.max(e.i,e.j);
      positive[e.t].set(`${a},${b}`,{pair:[a,b],weight:1+1e-4*tensor.get(e.t,a,b)});
    }
    const ts=JSON.parse(readFileSync(tsout,'utf8'));
    if(ts.matching.length!==16||ts.formation_pairs_by_tick.length!==16)throw new Error('MISSING_TICKS');
    for(let t=0;t<16;t++){
      const baseline=ts.matching[t],pairs=ts.formation_pairs_by_tick[t],graph=[...positive[t].values()];
      const base=baseline.residual,card=baseline.cardinality;
      if(card!==pairs.length || baseline.certified!==true)throw new Error('BASELINE_MISMATCH');
      let tested=0,ambiguous=false,witness=null,minGap=null,otherErrors=[];
      const started=performance.now();
      for(const [a,b] of pairs){
        const without=graph.filter(e=>!(e.pair[0]===a && e.pair[1]===b));
        try{
          const alt=matching(nodes,without,{maxEdges:6000,maxWallMs:2500});
          if(!alt.certified_optimality)throw new Error('NO_DUAL_CERT');
          tested++;
          const same=alt.cardinality===card && alt.exact_weight_residue===base;
          if(alt.cardinality>card||(alt.cardinality===card && alt.exact_weight_residue>base))
            throw new Error(`ALTERNATIVE_BETTER_THAN_FROZEN_ORIGINAL:${seed}:${k}:${t}`);
          if(same){
            ambiguous=true;witness={forbidden_edge:[a,b],other_optimum:alt.pairs,
              objective_cardinality:alt.cardinality,exact_integer_residue:alt.exact_weight_residue};
            break; // one distinct equal-valued certificate suffices to prove non-uniqueness
          }
          if(alt.cardinality===card){
            const gap=base-alt.exact_weight_residue;
            if(gap<=0)throw new Error('NONPOSITIVE_EQUAL_CARDINALITY_GAP');
            minGap=minGap===null?gap:Math.min(minGap,gap);
          }
        }catch(e){otherErrors.push({forbidden_edge:[a,b],error:String(e)});break;}
      }
      results.push({seed,scenario:input.scenario_order[k],t,cardinality:card,residual:base,
        candidate_edges:graph.length,selected_edges:pairs.length,
        exclusion_oracles_tested:tested,proven_nonunique:ambiguous,
        proven_unique:!ambiguous && !otherErrors.length && tested===pairs.length,
        unresolved:otherErrors.length>0,witness,strict_equal_cardinality_margin:minGap,
        error:otherErrors.length?otherErrors[0]:null,
        elapsed_ms:Math.round((performance.now()-started)*1000)/1000});
    }
  }
}
const complete=results.length===960;
const body={schema:'N344_ALL960_MATCH_OPTIMUM_UNIQUENESS',method:'EXCLUDE_EACH_SELECTED_EDGE_AND_SOLVE_EXACT_INTEGER',
  relation:'N343 verifies all original JS matching graph optimal values before N344',
  original_native_index_sha:sha(join(root,'outcomes','N342_NATIVE_INDEX.json')),
  original_js_index_sha:sha(join(root,'outcomes','N341_TS60_INDEX.json')),
  cases:results,complete,
  proven_unique:results.filter(x=>x.proven_unique).length,
  proven_nonunique:results.filter(x=>x.proven_nonunique).length,
  unresolved:results.filter(x=>x.unresolved).length,
  total_forbidden_edge_optimizations:results.reduce((s,x)=>s+x.exclusion_oracles_tested,0),
  CT2_scientific:7,STOP_R5_human:true};
writeFileSync(output,JSON.stringify(body,null,2)+'\n',{flag:'wx'});
console.log('N344_OPTIMUM_UNIQUENESS',results.length,'unique',body.proven_unique,
  'nonunique',body.proven_nonunique,'unresolved',body.unresolved,
  'exact forbidden-edge solves',body.total_forbidden_edge_optimizations);
