// N350: prospective falsification attempts against the integer Blossom dual proof.
// Uses ONLY the preexisting N339 12 graph inputs and witness outputs, NEVER reruns
// solver or edits previously frozen data. All controls/mutants preregistered.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {verifyDual} from '../work/src/blossom_matching.mjs';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const A=JSON.parse(readFileSync(join(root,'GRAPH_INPUTS_N339.json'),'utf8'));
const R=JSON.parse(readFileSync(join(root,'outcomes','N339_POLY_GRAPHS.json'),'utf8'));
const dest=join(root,'outcomes','N350_ADVERSARIAL_DUAL.json');
if(existsSync(dest))throw new Error('NO_OVERWRITE');
if(A.cases.length!==12||R.rows.length!==12)throw new Error('SOURCE_COUNT_DRIFT');
const SCALE=2**52;
const sha=x=>createHash('sha256').update(readFileSync(x)).digest('hex');
const expected={inputs:'875d3fdc70f07ae65c906221d8e7c8c4b37cbeb5106939c41604ba0d3bd1378b',
outcomes:'b7d3f483e90e956129e7197c72a23096512b4faff0facc34344cd5cd96951a2a'};
if(sha(join(root,'GRAPH_INPUTS_N339.json'))!==expected.inputs||
sha(join(root,'outcomes','N339_POLY_GRAPHS.json'))!==expected.outcomes)throw new Error('FROZEN_SOURCE_HASH_DRIFT');
const clone=x=>JSON.parse(JSON.stringify(x));
const key=(a,b)=>a<b? a+','+b:b+','+a;
const attacks=[];
for(let k=0;k<12;k++){
 const {name,edges}=A.cases[k],ans=R.rows[k].outcome;
 if(name!==R.rows[k].name||R.rows[k].status!=='EXECUTED')throw new Error('CASE_MISMATCH');
 const witness=ans.dual_witness;
 const original={nVertex:witness.n,dualVar:witness.dual,
  blossomParent:witness.parent,blossomBase:witness.base,
  blossomChilds:witness.childs};
 const weights=new Map(edges.map(([a,b,w])=>[key(a,b),ans.baseline_integer+(w-1)*SCALE]));
 const pairs=clone(ans.pairs),bound=Math.floor(A.cases[k].n/2)*(ans.baseline_integer+
 Math.max(...edges.map(x=>(x[2]-1)*SCALE)));
 const legit=verifyDual(clone(original),new Map(weights),clone(pairs),bound);
 if(!legit.certified)throw new Error('LEGIT_CERT_REJECTED');
 const mutations=[
 ['swap_first_matched_endpoint',s=>{
   if(s.pairs.length){s.pairs[0][1]=s.pairs[0][0];}
 }],
 ['duplicate_first_matched_pair',s=>{
   if(s.pairs.length)s.pairs.push([...s.pairs[0]]);
 }],
 ['first_matched_edge_weight_plus_one',s=>{
   if(s.pairs.length){const p=s.pairs[0],kk=key(...p);s.weights.set(kk,s.weights.get(kk)+1);}
 }],
 ['first_matched_edge_weight_minus_one',s=>{
   if(s.pairs.length){const p=s.pairs[0],kk=key(...p);s.weights.set(kk,s.weights.get(kk)-1);}
 }],
 ['dual_first_vertex_plus_one',s=>{s.dual.dualVar[0]+=1;}],
 ['dual_first_positive_vertex_minus_one',s=>{
   const i=s.dual.dualVar.findIndex((x,i)=>i<original.n&&x>0);
   if(i>=0)s.dual.dualVar[i]-=1;
 }],
 ['upper_bound_below_primal',s=>{
   s.bound=s.pairs.reduce((v,[a,b])=>v+s.weights.get(key(a,b)),0)-1;
 }],
 ['positive_blossom_dual_minus_one',s=>{
   const i=s.dual.dualVar.findIndex((x,i)=>i>=original.n&&x>0);
   if(i>=0)s.dual.dualVar[i]-=1;
 }],
 ['positive_blossom_dual_negative',s=>{
   const i=s.dual.dualVar.findIndex((x,i)=>i>=original.n&&x>0);
   if(i>=0)s.dual.dualVar[i]=-1;
 }],
 ['blossom_parent_self_loop',s=>{
   const i=s.dual.blossomParent.findIndex(x=>x>=original.n);
   if(i>=0)s.dual.blossomParent[i]=i;
 }],
 ['nonedge_in_matching',s=>{
   if(s.pairs.length){s.pairs[0]=[s.pairs[0][0],original.n+1];}
 }],
 ];
 for(const [kind,fn] of mutations){
   const state={dual:clone(original),weights:new Map(weights),pairs:clone(pairs),bound};
   fn(state);
   const changed=JSON.stringify(state.dual)!==JSON.stringify(original)||
    JSON.stringify(state.pairs)!==JSON.stringify(pairs)||state.bound!==bound||
    [...state.weights].some(([kk,v])=>weights.get(kk)!==v);
   if(!changed){attacks.push({name,attack:kind,status:'NOT_APPLICABLE_NO_MUTATION'});continue;}
   try{
     const result=verifyDual(state.dual,state.weights,state.pairs,state.bound);
     attacks.push({name,attack:kind,status:'ESCAPED',message:'Mutant claimed certified',certified:result.certified});
   }catch(e){attacks.push({name,attack:kind,status:'DETECTED',error:String(e).slice(0,230)});}
 }
}
const total=attacks.filter(a=>a.status!=='NOT_APPLICABLE_NO_MUTATION');
const output={schema:'ABH_N350_ADVERSARIAL_CERTIFICATE_FALSIFICATION',parent_N339_graph_input_sha:expected.inputs,
 parent_N339_result_sha:expected.outcomes,legitimate_certificates_checked:12,
 total_attacks:attacks.length,applicable_attacks:total.length,
 detected:total.filter(x=>x.status==='DETECTED').length,
 escaped:total.filter(x=>x.status==='ESCAPED').length,
 not_applicable:attacks.filter(x=>x.status==='NOT_APPLICABLE_NO_MUTATION').length,
 cases:attacks,CT2_scientific:7,STOP_R5_human:true};
writeFileSync(dest,JSON.stringify(output,null,2)+'\n',{flag:'wx'});
console.log('N350_MUTANTS',output.detected,'/',output.applicable_attacks,'rejected','escaped',output.escaped);
