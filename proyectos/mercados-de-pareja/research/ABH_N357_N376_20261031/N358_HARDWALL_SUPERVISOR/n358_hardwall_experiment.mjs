// N358 prospective strong resource-bound tests, with real child process controls.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runBounded} from './n358_hardwall_runner.mjs';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const output=join(root,'outcomes','N358_HARD_WALL_RESULTS.json');
if(existsSync(output))throw new Error('NO_OVERWRITE');
const hash=f=>createHash('sha256').update(readFileSync(f)).digest('hex');
function graph(name,n,edges){return {name,mode:'matching',nodes:Array.from({length:n},(_,i)=>i),edges};}
const fixtures=[
 graph('EMPTY_144',144,[]),
 graph('STAR_144',144,Array.from({length:143},(_,i)=>({pair:[0,i+1],weight:1+(i%91)*2**-52}))),
];
const edges=[];
for(let i=0;i<144;i++)for(let j=i+1;j<144;j++){
 const x=(i*1664525+j*1013904223)>>>0;
 if(x%1000<95)edges.push({pair:[i,j],weight:1+(x%37)*2**-52});
}
fixtures.push(graph('SPARSE_N144',144,edges));
const cases=[];
function check(name,request,options,expectedStatus,upperMs){
 const begin=performance.now();
 const result=runBounded(request,options);
 const elapsed=Math.round((performance.now()-begin)*1000)/1000;
 const good=result.status===expectedStatus &&
  (expectedStatus==='PASS'?result.certified===true:result.certified===false) &&
  elapsed<upperMs;
 if(!good)throw new Error('FAILED_CONTROL:'+name+':'+result.status+':elapsed='+elapsed);
 cases.push({name,status:result.status,expectedStatus,elapsed_ms:elapsed,
  wall_limit_ms:options.maxWallMs,probed_HARD_timeout:expectedStatus==='RESOURCE_HARD_WALL',
  certified:result.certified,
  ...(result.answer?{matching:{
   cardinality:result.answer.cardinality,pairs:result.answer.pairs,
   exact_weight_residue:result.answer.exact_weight_residue,
   full_units_decimal:result.answer.full_units_in_2_power_minus52,
   certificate:result.answer.certificate
  },edges:request.edges}:{}),
  input_vertices:request.nodes?.length??null,input_edges:request.edges?.length??null});
}
for(const f of fixtures)check(f.name,f,{maxWallMs:9000,maxHeapMB:128},'PASS',9000);
check('FORCED_CPU_STALL',{mode:'stall'},{maxWallMs:300,maxHeapMB:96},
 'RESOURCE_HARD_WALL',1750);
check('BUDGET_1MS_MATCHING',fixtures[2],{maxWallMs:1,maxHeapMB:128},
 'RESOURCE_HARD_WALL',1700);
check('CORRUPT_WORKER_JSON',{mode:'corrupt_json'},{maxWallMs:4000,maxHeapMB:96},
 'INVALID_WORKER_JSON',4000);
check('WORKER_CRASH',{mode:'crash'},{maxWallMs:4000,maxHeapMB:96},
 'WORKER_FAILURE',4000);
check('OUTPUT_OVERFLOW',{mode:'large_output'},{maxWallMs:4000,maxHeapMB:96,maxOutputBytes:2048},
 'RESOURCE_OUTPUT',4000);
if(cases.length!==8)throw new Error('CONTROL_COUNT_DRIFT');
const result={schema:'ABH_N358_EXTERNAL_HARD_WALL_PROSPECTIVE_V1',
 cases,valid_controls:cases.length,matching_controls_passed:3,
 preemption_controls_passed:2,rejected_invalid_worker_controls:3,
 source_sha256:{runner:hash(join(root,'instrument','n358_hardwall_runner.mjs')),
 worker:hash(join(root,'instrument','n358_hardwall_worker.mjs')),
 source_matching:hash(join(root,'work','src','blossom_matching.mjs'))},
 limits:{max_input_bytes:1048576,typical_max_output_bytes:262144,
 max_child_heap_mb:128,maximum_expected_wall_ms:9000},
 scientific_CT2:7,STOP_R5_human:true,not_human_validation:true};
writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log('N358_CONTROLS',cases.length,cases.map(x=>x.status).join(','),
 hash(output));
