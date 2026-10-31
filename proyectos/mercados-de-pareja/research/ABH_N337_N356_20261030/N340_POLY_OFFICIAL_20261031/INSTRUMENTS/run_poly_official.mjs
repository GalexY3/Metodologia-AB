// N340: actual full official N144/T16/K7 TypeScript event engine, replacing only matching.
// Source shocks & original Python comparison are frozen from the distinct N338 negative.
import { readFileSync,writeFileSync,existsSync } from 'node:fs';
import { dirname,join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { replay } from '../work/src/engine.ts';
import { scenarios } from '../work/src/types.ts';
import { readFloat64LE } from '../work/src/io.ts';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const prev=join(root,'../ESBM_AUDIT_N337_20261031');
const manifest=JSON.parse(readFileSync(join(prev,'N338_INPUT_MANIFEST.json'),'utf8'));
if(manifest.seed!==101 || manifest.N!==144 || manifest.T!==16 || manifest.K!==7 ||
   JSON.stringify(manifest.scenarios)!==JSON.stringify(['mixed_random','private_rejection_learning']))
   throw new Error('N340_INPUT_PLAN_CHANGED');
const tensors={};
for(const kind of ['u_send','u_reply','u_hazard','u_expose','u_match']) {
  const f=manifest.files[kind];
  tensors[kind]=readFloat64LE(join(prev,'official_101',f.name),f.sha256,f.shape);
}
const p=manifest.files.people;
const people=JSON.parse(readFileSync(join(prev,'official_101',p.name),'utf8'));
const outFile=join(root,'outcomes','N340_POLY_OFFICIAL_FULL.json');
if(existsSync(outFile))throw new Error('NO_OUTPUT_OVERWRITE');
const rows=[];
for(const name of manifest.scenarios) {
  const formed=[],matching=[],directed=[],tickSummary=[],graphShas=[];
  let eventCount=0,last=null;
  const start=performance.now();
  try {
    const run=replay(people,(kind,t,i,j)=>tensors[kind].get(t,i,j),
      scenarios[name],101,name,16,7,e=>{
        eventCount++;last={seq:e.seq,t:e.t,stage:e.stage,sender:e.sender,receiver:e.receiver};
        if(e.stage==='formation')formed.push(e.observed.pairs.map(([a,b])=>[Math.min(a,b),Math.max(a,b)]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
        if(e.stage==='matching') {
          matching.push({t:e.t,certified:e.solver_meta?.certified_optimality??false,
            uniqueness:e.solver_meta?.uniqueness_status??null,
            certificate:e.solver_meta?.certificate??null,
            cardinality:e.observed.cardinality,
            residue:e.solver_meta?.exact_weight_residue??null});
        }
        if(e.stage==='matching_graph'){
          const bytes=JSON.stringify(e.observed.edges);
          graphShas.push({t:e.t,sha256:createHash('sha256').update(bytes).digest('hex'),edges:e.observed.edges.length});
        }
        if(e.stage==='track')tickSummary.push(e.observed.track);
        if(['exposure','proposal','response','dissolution'].includes(e.stage)){
          const o=e.observed;
          directed.push({t:e.t,seq:e.seq,stage:e.stage,i:e.sender,j:e.receiver,
            decision:e.stage==='proposal'?o.proposes:e.stage==='response'?o.accepted:e.stage==='dissolution'?o.dissolve:null,
            ...(e.u===undefined?{}:{u:e.u}),...(e.p===undefined?{}:{p:e.p})});
        }
      },{maxEdges:6000,maxWallMs:5000},
      {maxEvents:80000,maxBytes:134217728});
    rows.push({seed:101,scenario:name,status:'EXECUTED',result:run.result,
      formation_pairs_by_tick:formed,matching,graphShas,directed,tickSummary,
      event_count:eventCount,elapsed_ms:Math.round((performance.now()-start)*1000)/1000});
  } catch(e) {rows.push({seed:101,scenario:name,status:'NEGATIVE',error:String(e),
    formation_pairs_by_tick:formed,matching,graphShas,directed,tickSummary,
    event_count:eventCount,last_event:last,elapsed_ms:Math.round((performance.now()-start)*1000)/1000});}
}
writeFileSync(outFile,JSON.stringify({schema:'ABH_N340_OFFICIAL_POLY_JS_RESULT',
  data_source:'Frozen N338 official original Python tensors SHA; original code untouched',rows},null,2)+'\n',{flag:'wx'});
console.log('N340_OFFICIAL',rows.map(x=>x.scenario+':'+x.status+':'+x.formation_pairs_by_tick.length+'ticks/'+x.event_count+'events').join(' '));
