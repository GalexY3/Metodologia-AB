// N348 complete dynamic ESBM alternative allocation mechanism trajectories.
// Same N144/T16/K7 synthetic people and five fixed PCG64 shocks per seed.
// Two independent orders (chronological, reverse); outcomes feed next-tick state.
// This is mechanistic simulation, never human dating validation.
import {readFileSync,writeFileSync,openSync,writeSync,closeSync,mkdirSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {replay} from '../work/src/engine_decentralized.ts';
import {scenarios} from '../work/src/types.ts';
import {readFloat64LE,checkedBytes} from '../work/src/io.ts';
import {matching as decentralizedMatching} from '../work/src/decentralized_matching.mjs';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const manifestFile=join(root,'N341_INPUT_MANIFEST.json');
const plan=JSON.parse(readFileSync(manifestFile,'utf8'));
const required=[101,211,307,401,503,601];
const names=['mixed_random','heterosexual_restricted','institutional_segregation',
 'explicit_norm_preference','popularity_ranking','visibility_balancing',
 'private_rejection_learning','public_rejection_signal',
 'longer_partnerships','shorter_partnerships'];
const orders=['chronological','reverse'];
if(plan.schema!=='ABH_N341_ORIGINAL_INPUTS_FROZEN'||plan.n!==144||plan.t!==16||plan.k!==7||
  JSON.stringify(plan.seed_order)!==JSON.stringify(required)||
  JSON.stringify(plan.scenario_order)!==JSON.stringify(names)||
  JSON.stringify(Object.keys(scenarios))!==JSON.stringify(names))throw new Error('PLAN_CHANGED');
const hash=x=>createHash('sha256').update(x).digest('hex');
const outputDir=join(root,'outcomes','N348_DECENTRALIZED_TRACES');
const indexFile=join(root,'outcomes','N348_DECENTRALIZED_INDEX.json');
if(existsSync(outputDir)||existsSync(indexFile))throw new Error('OUTCOME_ALREADY_EXISTS');
// Adversarial fail-closed test of invalid pair input, before starting real runs.
let errorCode=null;
try{decentralizedMatching([1,2],[[1,1]],'chronological');}catch(e){errorCode=String(e);}
if(!errorCode?.includes('INVALID_ACCEPTANCE_EDGE'))throw new Error('SELF_EDGE_NEGATIVE_CONTROL_FAILED');
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
      const formation=[],tracks=[];let events=0,directed=0;const hashStream=createHash('sha256');
      const start=performance.now();let receipt;
      try{
        const out=replay(people,(kind,t,i,j)=>tensor[kind].get(t,i,j),
          scenarios[name],seed,name,16,7,
          e=>{
            events++;
            if(e.stage==='formation')formation.push(e.observed.pairs.map(([a,b])=>[Math.min(a,b),Math.max(a,b)]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
            if(e.stage==='track')tracks.push(e.observed.track);
            if(['exposure','proposal','response','dissolution'].includes(e.stage)){
              const o=e.observed;
              const ev={seed,scenario:name,order,t:e.t,seq:e.seq,stage:e.stage,i:e.sender,j:e.receiver,
                decision:e.stage==='proposal'?o.proposes:e.stage==='response'?o.accepted:e.stage==='dissolution'?o.dissolve:null,
                ...(e.u===undefined?{}:{u:e.u}),...(e.p===undefined?{}:{p:e.p})};
              const line=JSON.stringify(ev)+'\n';writeSync(fd,line,'utf8');hashStream.update(line);directed++;
            }
          },undefined,{maxEvents:80000,maxBytes:134217728},order);
        receipt={schema:'ABH_N348_INDIVIDUAL_DYNAMIC_RESULT',seed,scenario:name,order,status:'EXECUTED',
          result:out.result,formation_pairs_by_tick:formation,tracks,
          total_events:events,directed_events:directed,
          elapsed_ms:Math.round((performance.now()-start)*1000)/1000};
      }catch(e){receipt={schema:'ABH_N348_INDIVIDUAL_DYNAMIC_RESULT',seed,scenario:name,order,
        status:'NEGATIVE',error:String(e),formation_pairs_by_tick:formation,tracks,
        total_events:events,directed_events:directed,
        elapsed_ms:Math.round((performance.now()-start)*1000)/1000};}
      finally{closeSync(fd)}
      writeFileSync(receiptPath,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
      rows.push({seed,scenario:name,order,status:receipt.status,
        run_file:`N348_DECENTRALIZED_TRACES/${label}.json`,
        run_sha256:hash(readFileSync(receiptPath)),
        trace_file:`N348_DECENTRALIZED_TRACES/${label}.jsonl`,
        trace_sha256:hashStream.digest('hex'),
        matching_ticks:formation.length,directed_events:directed,total_events:events,
        elapsed_ms:receipt.elapsed_ms,...(receipt.status==='NEGATIVE'?{error:receipt.error}:{})});
    }
  }
}
const index={schema:'ABH_N348_DYNAMIC_DECENTRALIZED_INDEX',
  frozen_original_input_manifest_sha256:hash(readFileSync(manifestFile)),
  orders,seed_order:required,scenarios:names,expected_runs:120,
  negative_control_invalid_edge_detected:errorCode,rows};
writeFileSync(indexFile,JSON.stringify(index,null,2)+'\n',{flag:'wx'});
console.log('N348_DYNAMIC_COMPLETE',rows.filter(x=>x.status==='EXECUTED').length,'/120',
  '16tick',rows.filter(x=>x.matching_ticks===16).length,
  'directed',rows.reduce((s,x)=>s+x.directed_events,0));
