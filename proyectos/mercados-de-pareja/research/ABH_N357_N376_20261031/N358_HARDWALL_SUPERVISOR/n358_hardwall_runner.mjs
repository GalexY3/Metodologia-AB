// AB-H N358: bounded process-isolated adapter. Does not modify original ESBM.
// A synchronous Blossom run cannot be interrupted by a timer on the same event loop.
import {spawnSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const worker=join(root,'instrument','n358_hardwall_worker.mjs');
export function runBounded(request,options={}){
 const wall=options.maxWallMs??5000;
 const outputCap=options.maxOutputBytes??262144;
 const inputCap=options.maxInputBytes??1048576;
 const heapMB=options.maxHeapMB??96;
 if(!Number.isSafeInteger(wall)||wall<1||wall>30000)throw new Error('INVALID_WALL_LIMIT');
 if(!Number.isSafeInteger(outputCap)||outputCap<100||outputCap>1048576)throw new Error('INVALID_OUTPUT_LIMIT');
 if(!Number.isSafeInteger(inputCap)||inputCap<100||inputCap>4194304)throw new Error('INVALID_INPUT_LIMIT');
 if(!Number.isSafeInteger(heapMB)||heapMB<32||heapMB>512)throw new Error('INVALID_HEAP_LIMIT');
 const payload=JSON.stringify(request);
 if(Buffer.byteLength(payload)>inputCap)return {status:'RESOURCE_INPUT',certified:false};
 const result=spawnSync(process.execPath,[`--max-old-space-size=${heapMB}`,worker],{
  input:payload,encoding:'utf8',timeout:wall,maxBuffer:outputCap,windowsHide:true
 });
 if(result.error){
  if(result.error.code==='ETIMEDOUT')return {status:'RESOURCE_HARD_WALL',certified:false,error_code:'ETIMEDOUT'};
  if(result.error.code==='ENOBUFS')return {status:'RESOURCE_OUTPUT',certified:false,error_code:'ENOBUFS'};
  return {status:'WORKER_FAILURE',certified:false,error_code:result.error.code||'UNKNOWN'};
 }
 if(result.status!==0)return {status:'WORKER_FAILURE',certified:false,exit_code:result.status};
 let data;
 try{data=JSON.parse(result.stdout);}catch{return {status:'INVALID_WORKER_JSON',certified:false};}
 if(!data||data.status!=='MATCHING_COMPLETED'||data.answer?.certified_optimality!==true||
  data.answer?.full_units_format!=='decimal_bigint_string'||
  typeof data.answer?.full_units_in_2_power_minus52!=='string'||
  !/^[0-9]+$/.test(data.answer.full_units_in_2_power_minus52)||
  !Number.isSafeInteger(data.answer?.exact_weight_residue))
  return {status:'INVALID_WORKER_SCHEMA',certified:false};
 return {status:'PASS',certified:true,answer:data.answer};
}
