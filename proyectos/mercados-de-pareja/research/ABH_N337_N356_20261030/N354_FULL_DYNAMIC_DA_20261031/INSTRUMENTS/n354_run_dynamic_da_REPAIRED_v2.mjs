// N354 full dynamic ESBM conditional Gale-Shapley alternative institution.
// Same N144/T16/K7 synthetic people and five fixed PCG64 shocks per seed.
// Two independent orders (chronological, reverse); outcomes feed next-tick state.
// This is mechanistic simulation, never human dating validation.
import {readFileSync,writeFileSync,openSync,writeSync,closeSync,mkdirSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {replay} from '../work/src/engine_DA.ts';
import {scenarios} from '../work/src/types.ts';
import {readFloat64LE,checkedBytes} from '../work/src/io.ts';
import {matching as daMatching} from '../work/src/da_matching.mjs';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const manifestFile=join(root,'N341_INPUT_MANIFEST.json');
const plan=JSON.parse(readFileSync(manifestFile,'utf8'));
const required=[101,211,307,401,503,601];
const names=['heterosexual_restricted'];
const orders=['chronological','reverse'];
if(plan.schema!=='ABH_N341_ORIGINAL_INPUTS_FROZEN'||plan.n!==144||plan.t!==16||plan.k!==7||
  JSON.stringify(plan.seed_order)!==JSON.stringify(required)||
  JSON.stringify(plan.scenario_order)!==JSON.stringify(Object.keys(scenarios))||
  names.some(name=>!Object.prototype.hasOwnProperty.call(scenarios,name)))
  throw new Error('PLAN_CHANGED');
const hash=x=>createHash('sha256').update(x).digest('hex');
const outputDir=join(root,'outcomes','N354_DA_DYNAMIC_TRACES');
const indexFile=join(root,'outcomes','N354_DA_DYNAMIC_INDEX.json');
if(existsSync(outputDir)||existsSync(indexFile))throw new Error('OUTCOME_ALREADY_EXISTS');
// Adversarial fail-closed test of invalid pair input, before starting real runs.
let errorCode=null;
try{daMatching([0,1],[[0,0]],{genders:['F','M'],q:[0.5,0.5],
  age:[20,20],norm:[0,0]},0,'F');}catch(e){errorCode=String(e);}
if(!errorCode?.includes('DA_INVALID_ACCEPTANCE_EDGE'))throw new Error('DA_SELF_EDGE_NEGATIVE_CONTROL_FAILED');
mkdirSync(outputDir,{recursive:true});
const rows=[];
for(const seedrow of plan.rows){
  const seed=seedrow.seed,src=join(root,'official_inputs_60');
  const people=JSON.parse(checkedBytes(join(src,seedrow.people.path),seedrow.people.sha256,seedrow.people.bytes).toString('utf8'));
  const tensor={};
  for(const kind of ['u_send','u_reply','u_hazard','u_expose','u_match']){
    const f=seedrow.tensors[kind];tensor[kind]=readFloat64LE(join(src,f.path),f.sha256,f.shape);
  }
  for(const name of names){
    for(const order of orders){
      const label=`${seed}_${name}_${order}`;
      const path=join(outputDir,label+'.jsonl'),receiptPath=join(outputDir,label+'.json');
      const fd=openSync(path,'wx');
      const formation=[],tracks=[],matchingDiagnostics=[];let events=0,directed=0;const hashStream=createHash('sha256');
      const start=performance.now();let receipt;
      try{
        const out=replay(people,(kind,t,i,j)=>tensor[kind].get(t,i,j),
          scenarios[name],seed,name,16,7,
          e=>{
            events++;
            if(e.stage==='formation')formation.push(e.observed.pairs.map(([a,b])=>[Math.min(a,b),Math.max(a,b)]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
            if(e.stage==='track')tracks.push(e.observed.track);
            if(e.stage==='matching')matchingDiagnostics.push({
              t:e.t,pairs:e.observed.pairs,meta:e.solver_meta});
            if(['exposure','proposal','response','dissolution'].includes(e.stage)){
              const o=e.observed;
              const ev={seed,scenario:name,order,t:e.t,seq:e.seq,stage:e.stage,i:e.sender,j:e.receiver,
                decision:e.stage==='proposal'?o.proposes:e.stage==='response'?o.accepted:e.stage==='dissolution'?o.dissolve:null,
                ...(e.u===undefined?{}:{u:e.u}),...(e.p===undefined?{}:{p:e.p})};
              const line=JSON.stringify(ev)+'\n';writeSync(fd,line,'utf8');hashStream.update(line);directed++;
            }
          },undefined,{maxEvents:80000,maxBytes:134217728},order);
        receipt={schema:'ABH_N354_INDIVIDUAL_DYNAMIC_DA_RESULT',seed,scenario:name,
          order,proposer_side:order==='chronological'?'F':'M',status:'EXECUTED',
          result:out.result,formation_pairs_by_tick:formation,tracks,matchingDiagnostics,
          total_events:events,directed_events:directed,
          elapsed_ms:Math.round((performance.now()-start)*1000)/1000};
      }catch(e){receipt={schema:'ABH_N354_INDIVIDUAL_DYNAMIC_DA_RESULT',seed,scenario:name,
        order,proposer_side:order==='chronological'?'F':'M',
        status:'NEGATIVE',error:String(e),formation_pairs_by_tick:formation,tracks,matchingDiagnostics,
        total_events:events,directed_events:directed,
        elapsed_ms:Math.round((performance.now()-start)*1000)/1000};}
      finally{closeSync(fd)}
      writeFileSync(receiptPath,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
      rows.push({seed,scenario:name,order,status:receipt.status,
        run_file:`N354_DA_DYNAMIC_TRACES/${label}.json`,
        run_sha256:hash(readFileSync(receiptPath)),
        trace_file:`N354_DA_DYNAMIC_TRACES/${label}.jsonl`,
        trace_sha256:hashStream.digest('hex'),
        matching_ticks:formation.length,directed_events:directed,total_events:events,
        elapsed_ms:receipt.elapsed_ms,...(receipt.status==='NEGATIVE'?{error:receipt.error}:{})});
    }
  }
}
const index={schema:'ABH_N354_DYNAMIC_BIPARTITE_DA_INDEX',
  frozen_original_input_manifest_sha256:hash(readFileSync(manifestFile)),
  orders,proposer_side_map:{chronological:'F',reverse:'M'},
  seed_order:required,scenarios:names,expected_runs:12,
  negative_control_invalid_edge_detected:errorCode,rows};
writeFileSync(indexFile,JSON.stringify(index,null,2)+'\n',{flag:'wx'});
console.log('N354_DYNAMIC_DA_COMPLETE',rows.filter(x=>x.status==='EXECUTED').length,'/12',
  '16tick',rows.filter(x=>x.matching_ticks===16).length,
  'directed',rows.reduce((s,x)=>s+x.directed_events,0));
