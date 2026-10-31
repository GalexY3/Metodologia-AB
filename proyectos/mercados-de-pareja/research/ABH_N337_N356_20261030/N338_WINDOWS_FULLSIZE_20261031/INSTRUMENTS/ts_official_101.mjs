// Run the actual local N207 TypeScript engine at full official 144x16x7 input size.
// A resource stop is an outcome; no fallback or alteration of the original engine.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { replay } from './installer_review/unpacked/windows-replica/src/engine.ts';
import { scenarios } from './installer_review/unpacked/windows-replica/src/types.ts';
import { readFloat64LE } from './installer_review/unpacked/windows-replica/src/io.ts';
const root=dirname(fileURLToPath(import.meta.url));
const manifest=JSON.parse(readFileSync(join(root,'N338_INPUT_MANIFEST.json'),'utf8'));
if(manifest.N!==144 || manifest.T!==16 || manifest.K!==7) throw new Error('INVALID_OFFICIAL_SHAPE');
const base=join(root,'official_101');
const people=JSON.parse(readFileSync(join(base,manifest.files.people.name),'utf8'));
const tensorNames=['u_send','u_reply','u_hazard','u_expose','u_match'];
const tensors={};
for(const name of tensorNames){
  const entry=manifest.files[name];
  tensors[name]=readFloat64LE(join(base,entry.name),entry.sha256,entry.shape);
}
const outPath=join(root,'N338_TS_OFFICIAL.json');
if(existsSync(outPath)) throw new Error('OUTPUT_PREEXISTS');
const results=[];
for(const name of manifest.scenarios){
  const pairs=[], status=[];
  let seenEvents=0, lastEvent=null;
  try{
    const out=replay(people,(kind,t,i,j)=>tensors[kind].get(t,i,j),
      scenarios[name],101,name,16,7,e=>{
        seenEvents++;
        if(e.stage==='formation') pairs.push(e.observed.pairs.map(([a,b])=>[Math.min(a,b),Math.max(a,b)]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]));
        if(e.stage==='matching') status.push(e.solver_meta?.status??null);
        lastEvent={t:e.t,stage:e.stage,sender:e.sender,receiver:e.receiver,seq:e.seq};
      },{maxStates:50000,maxComponentNodes:22,maxWallMs:2500,maxHeapBytes:524288000},
        {maxEvents:80000,maxBytes:134217728});
    results.push({seed:101,scenario:name,status:'EXECUTED',result:out.result,
      formation_pairs_by_tick:pairs,matching_status:status,emitted_events:seenEvents});
  }catch(e){
    results.push({seed:101,scenario:name,status:'EXECUTED_NEGATIVE',error:String(e),
      formation_pairs_by_tick:pairs,matching_status:status,emitted_events:seenEvents,last_event:lastEvent});
  }
}
writeFileSync(outPath,JSON.stringify({schema:'N338_TS_N207_OFFICIAL_N144',runs:results},null,2)+'\n',{flag:'wx'});
console.log('N338_TS_OFFICIAL',results.map(x=>`${x.scenario}:${x.status}:${x.emitted_events}`).join(' '));
