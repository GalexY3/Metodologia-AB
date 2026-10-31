// Conditional Gale–Shapley with declared STRICT synthetic ordinal preferences.
// Only acts on native artificial F-M mutual-acceptance opportunities.
import { candidateEdges } from './matching.ts';
export { candidateEdges };
const canonical=([a,b])=>a<b?[a,b]:[b,a];
export function matching(available, acceptedDirected, p, t, proposerSide='F'){
 if(!['F','M'].includes(proposerSide))throw new Error('DA_INVALID_PROPOSING_SIDE');
 const set=new Set(available),edges=new Set(),listed=new Map();
 for(const [i,j] of acceptedDirected){
   if(!set.has(i)||!set.has(j)||i===j)throw new Error('DA_INVALID_ACCEPTANCE_EDGE');
   if(!((p.genders[i]==='F'&&p.genders[j]==='M')||(p.genders[i]==='M'&&p.genders[j]==='F')))
     throw new Error('DA_NONBIPARTITE_ACCEPTANCE');
   const a=Math.min(i,j),b=Math.max(i,j),key=String(a)+','+String(b);
   if(edges.has(key))continue;
   edges.add(key);
   if(!listed.has(i))listed.set(i,[]);
   if(!listed.has(j))listed.set(j,[]);
   listed.get(i).push(j);listed.get(j).push(i);
 }
 const prefs=new Map();
 for(const [i,partners] of listed){
   const score=j=>Math.round((p.q[j]-0.02*Math.abs(p.age[i]-p.age[j])+
         0.03*Number(p.norm[i]===p.norm[j])-1e-7*j)*1e12)/1e12;
   prefs.set(i,[...partners].sort((a,b)=>score(b)-score(a)||a-b));
 }
 const proposers=[...listed.keys()].filter(i=>p.genders[i]===proposerSide).sort((a,b)=>a-b);
 const pos=new Map([...listed.keys()].map(i=>[i,new Map((prefs.get(i)||[]).map((j,k)=>[j,k]))]));
 const next=new Map(proposers.map(i=>[i,0])),free=[...proposers],holder=new Map();
 let proposals=0;
 while(free.length){
   const i=free.shift(),partners=prefs.get(i)||[],index=next.get(i);
   if(index>=partners.length)continue;
   const j=partners[index];next.set(i,index+1);proposals++;
   if(proposals>edges.size+1)throw new Error('DA_PROPOSALS_EXCEED_ACCEPTED_EDGES');
   if(!pos.get(j)?.has(i))throw new Error('DA_ONE_SIDED_PREFERENCE');
   const current=holder.get(j);
   if(current===undefined)holder.set(j,i);
   else if(pos.get(j).get(i)<pos.get(j).get(current)){
     holder.set(j,i);free.push(current);
   }else free.push(i);
 }
 const pairs=[...holder.entries()].map(([j,i])=>canonical([i,j])).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
 const partner=new Map(pairs.flatMap(([i,j])=>[[i,j],[j,i]]));
 let blocking=0;
 for(const key of edges){
   const [i,j]=key.split(',').map(Number);
   const better=(a,b)=>!partner.has(a)||pos.get(a).get(b)<pos.get(a).get(partner.get(a));
   if(better(i,j)&&better(j,i))blocking++;
 }
 if(blocking!==0)throw new Error('DA_BLOCKING_PAIRS:'+String(blocking));
 return {pairs,cardinality:pairs.length,unique:false,certified_optimality:false,
   method:'STABLE_GALE_SHAPLEY_CONDITIONAL_STRICT_ASSUMED_RANKS',
   preference_spec:'q_receiver_minus_age_gap_plus_norm_minus_id',
   proposer_side:proposerSide,blocking_pairs:0,proposals_used:proposals,
   accepted_undirected_edges:edges.size,statistical_validation:false};
}
