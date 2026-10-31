// Prospective N341 6x10 official N144/T16/K7 independent JS ESBM poly-matching runs.
// Writes compact directed events per run as separate JSONL, SHA checks every fixed input.
import {readFileSync,writeFileSync,openSync,writeSync,closeSync,existsSync,mkdirSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {replay} from '../work/src/engine.ts';
import {scenarios} from '../work/src/types.ts';
import {readFloat64LE,checkedBytes} from '../work/src/io.ts';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const manifestPath=join(root,'N341_INPUT_MANIFEST.json');
const input=JSON.parse(readFileSync(manifestPath,'utf8'));
const names=['mixed_random','heterosexual_restricted','institutional_segregation',
  'explicit_norm_preference','popularity_ranking','visibility_balancing',
  'private_rejection_learning','public_rejection_signal',
  'longer_partnerships','shorter_partnerships'];
const seeds=[101,211,307,401,503,601];
if(input.schema!=='ABH_N341_ORIGINAL_INPUTS_FROZEN'||input.n!==144||input.t!==16||input.k!==7||
   JSON.stringify(input.seed_order)!==JSON.stringify(seeds)||
   JSON.stringify(input.scenario_order)!==JSON.stringify(names)||
   JSON.stringify(Object.keys(scenarios))!==JSON.stringify(names))throw new Error('FROZEN_PLAN_CHANGED');
const inputSha=createHash('sha256').update(readFileSync(manifestPath)).digest('hex');
const outdir=join(root,'outcomes','N341_TRACES');
const summaryPath=join(root,'outcomes','N341_TS60_INDEX.json');
if(!existsSync(outdir)||existsSync(summaryPath))throw new Error('N341_RESUME_REQUIRES_PARTIAL_ONLY');
const partial=JSON.parse(readFileSync(join(root,'N341_PARTIAL_54_MANIFEST.json'),'utf8'));
if(partial.schema!=='N341_INTERRUPTED_FIRST54_HASH_CUSTODY'||partial.rows.length!==54||
  partial.frozen_original_input_manifest_sha256!==inputSha ||
  partial.frozen_original_JS_runner_sha256!=='90e5abec08338a1b2d12126d00cd7c89aa5d2677c8655d21f0eed8f35b2706d4')
  throw new Error('PARTIAL_CUSTODY_REPRODUCIBILITY_MISMATCH');
const completed=new Map(partial.rows.map(x=>[`${x.seed}_${x.scenario}`,x]));
const report=[];
for(const row of input.rows){
  const directory=join(root,'official_inputs_60');
  const people=JSON.parse(checkedBytes(join(directory,row.people.path),row.people.sha256,row.people.bytes).toString('utf8'));
  const tensors={};
  for(const kind of ['u_send','u_reply','u_hazard','u_expose','u_match']){
    const p=row.tensors[kind];
    tensors[kind]=readFloat64LE(join(directory,p.path),p.sha256,p.shape);
  }
  for(const name of names){
    const label=`${row.seed}_${name}`,eventPath=join(outdir,`${label}.jsonl`),runPath=join(outdir,`${label}.json`);
    const past=completed.get(label);
    if(past){
      if(!existsSync(runPath)||!existsSync(eventPath))throw new Error(`N341_PARTIAL_FILE_MISSING:${label}`);
      const oldRun=readFileSync(runPath),oldTrace=readFileSync(eventPath);
      const runSha=createHash('sha256').update(oldRun).digest('hex');
      const traceSha=createHash('sha256').update(oldTrace).digest('hex');
      if(runSha!==past.run_sha256||traceSha!==past.trace_sha256||
         oldRun.length!==past.run_bytes||oldTrace.length!==past.trace_bytes)
        throw new Error(`N341_PARTIAL_HASH_MISMATCH:${label}`);
      const old=JSON.parse(oldRun.toString('utf8'));
      if(old.status!=='EXECUTED'||old.formation_pairs_by_tick.length!==16||old.matching.length!==16||
         old.matching.some(m=>!m.certified||!m.certificate?.certified))
        throw new Error(`N341_PARTIAL_COMPLETION_NOT_VERIFIED:${label}`);
      report.push({seed:row.seed,scenario:name,status:old.status,
        run_file:`N341_TRACES/${label}.json`,run_sha256:runSha,
        trace_file:`N341_TRACES/${label}.jsonl`,trace_sha256:traceSha,
        formation_ticks:16,matching_certified:16,
        directed_events:old.directed_count,total_events:old.event_count,elapsed_ms:old.elapsed_ms});
      continue;
    }
    if(existsSync(runPath)||existsSync(eventPath))throw new Error(`N341_UNEXPECTED_PARTIAL_FILE:${label}`);
    const fd=openSync(eventPath,'wx');
    let directedCount=0,eventCount=0,lastEvent=null;
    const eventHash=createHash('sha256'),formation=[],matching=[],graphHashes=[];
    const start=performance.now();
    let output;
    try {
      try {
        const run=replay(people,(kind,t,i,j)=>tensors[kind].get(t,i,j),
          scenarios[name],row.seed,name,16,7,e=>{
            eventCount++;lastEvent={seq:e.seq,t:e.t,stage:e.stage,sender:e.sender,receiver:e.receiver};
            if(e.stage==='formation')formation.push(e.observed.pairs.map(([a,b])=>[Math.min(a,b),Math.max(a,b)]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
            if(e.stage==='matching')matching.push({t:e.t,certified:e.solver_meta?.certified_optimality??false,
              unique_proven:e.solver_meta?.unique??false,certificate:e.solver_meta?.certificate??null,
              cardinality:e.observed.cardinality,residual:e.solver_meta?.exact_weight_residue??null});
            if(e.stage==='matching_graph')graphHashes.push({t:e.t,sha256:createHash('sha256').update(JSON.stringify(e.observed.edges)).digest('hex'),edges:e.observed.edges.length});
            if(['exposure','proposal','response','dissolution'].includes(e.stage)){
              const o=e.observed;
              const record={seed:row.seed,scenario:name,t:e.t,seq:e.seq,stage:e.stage,i:e.sender,j:e.receiver,
                decision:e.stage==='proposal'?o.proposes:e.stage==='response'?o.accepted:e.stage==='dissolution'?o.dissolve:null,
                ...(e.u===undefined?{}:{u:e.u}),...(e.p===undefined?{}:{p:e.p})};
              const line=JSON.stringify(record)+'\n';
              eventHash.update(line);writeSync(fd,line,'utf8');directedCount++;
            }
          },{maxEdges:6000,maxWallMs:5000},
          {maxEvents:80000,maxBytes:134217728});
        output={schema:'N341_JS_TS_RUN',seed:row.seed,scenario:name,status:'EXECUTED',result:run.result,
          formation_pairs_by_tick:formation,matching,graphHashes,
          event_count:eventCount,directed_count:directedCount,
          elapsed_ms:Math.round((performance.now()-start)*1000)/1000};
      } catch(e) {
        output={schema:'N341_JS_TS_RUN',seed:row.seed,scenario:name,status:'NEGATIVE',error:String(e),
          formation_pairs_by_tick:formation,matching,graphHashes,last_event:lastEvent,
          event_count:eventCount,directed_count:directedCount,
          elapsed_ms:Math.round((performance.now()-start)*1000)/1000};
      }
    }finally{closeSync(fd)}
    writeFileSync(runPath,JSON.stringify(output,null,2)+'\n',{flag:'wx'});
    report.push({seed:row.seed,scenario:name,status:output.status,
      run_file:`N341_TRACES/${label}.json`,run_sha256:createHash('sha256').update(readFileSync(runPath)).digest('hex'),
      trace_file:`N341_TRACES/${label}.jsonl`,trace_sha256:eventHash.digest('hex'),
      formation_ticks:formation.length,matching_certified:matching.filter(x=>x.certified&&x.certificate?.certified).length,
      directed_events:directedCount,total_events:eventCount,elapsed_ms:output.elapsed_ms,
      ...(output.status==='NEGATIVE'?{error:output.error,last_event:output.last_event}:{})});
    // Avoid redirected-stdout deadlock: one final aggregate line only.
  }
}
writeFileSync(summaryPath,JSON.stringify({schema:'ABH_N341_JS60_RUN_INDEX',original_input_manifest_sha256:inputSha,
  seeds,scenario_order:names,expected_runs:60,rows:report},null,2)+'\n',{flag:'wx'});
console.log('N341_COMPLETED',report.filter(x=>x.status==='EXECUTED').length,'/60',
  'certified_ticks',report.reduce((n,x)=>n+x.matching_certified,0));
