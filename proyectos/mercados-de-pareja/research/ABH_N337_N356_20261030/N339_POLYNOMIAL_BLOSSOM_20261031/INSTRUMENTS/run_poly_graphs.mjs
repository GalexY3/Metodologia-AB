// Run the prefrozen graph suite through MIT Blossom with a checked primal-dual certificate.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {matching} from '../work/src/blossom_matching.mjs';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const input=JSON.parse(readFileSync(join(root,'GRAPH_INPUTS_N339.json'),'utf8'));
if(input.schema!=='ABH_N339_GRAPH_INPUTS_NO_OUTCOMES'||input.n_cases!==12)throw new Error('GRAPH_CASE_SET_CHANGED');
const output=join(root,'outcomes','N339_POLY_GRAPHS.json');
if(existsSync(output))throw new Error('NO_OUTPUT_OVERWRITE');
const rows=[];
for(const {name,n,edges} of input.cases){
  const start=performance.now();
  try{
    const ans=matching(Array.from({length:n},(_,i)=>i),edges.map(([a,b,w])=>({pair:[a,b],weight:w})),
      {maxEdges:5500,maxWallMs:30000,emitWitness:true});
    rows.push({name,n,edges:edges.length,status:'EXECUTED',outcome:ans,
      time_ms:Math.round((performance.now()-start)*1000)/1000});
  }catch(e){rows.push({name,n,edges:edges.length,status:'NEGATIVE',error:String(e),
    time_ms:Math.round((performance.now()-start)*1000)/1000});}
}
writeFileSync(output,JSON.stringify({schema:'ABH_N339_POLY_RESULT',rows},null,2)+'\n',{flag:'wx'});
console.log('N339_SOLVER_GRAPHS',rows.map(x=>x.name+':'+x.status).join(' '));
