// N348 first-accepted sequential partner assignment, not a maximum-weight
// or stable Gale-Shapley solution. Accepted response stream order is causal
// in this artificial protocol; we do not infer this rule from human decisions.
import { candidateEdges } from './matching.ts';
export { candidateEdges };

export function matching(available, acceptedDirected, order='chronological') {
  if(!['chronological','reverse'].includes(order))throw new Error('INVALID_DECENTRALIZED_ORDER');
  const eligible=new Set(available),used=new Set(),pairs=[];
  const decisions=order==='reverse'?[...acceptedDirected].reverse():acceptedDirected;
  for(const entry of decisions){
    const [i,j]=entry;
    if(!Number.isSafeInteger(i)||!Number.isSafeInteger(j)||i===j||!eligible.has(i)||!eligible.has(j))
      throw new Error('INVALID_ACCEPTANCE_EDGE');
    if(used.has(i)||used.has(j))continue;
    used.add(i);used.add(j);
    pairs.push(i<j?[i,j]:[j,i]);
  }
  pairs.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  return {pairs,cardinality:pairs.length,unique:false,
    certified_optimality:false,method:'IMMEDIATE_ACCEPTED_PAIRING_NOT_CENTRAL_SOLVER',
    protocol:order,temporal_choice_order_sensitivity:true};
}
