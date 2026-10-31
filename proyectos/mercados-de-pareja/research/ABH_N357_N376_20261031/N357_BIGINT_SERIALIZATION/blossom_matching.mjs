// AB-H prototype: integer-exact ESBM weight normalization and checkable primal-dual witness.
// Vendored EdmondsBlossom originally by Matt Krick, MIT, fixed upstream SHA in vendor/.
// Algorithm shares Joris van Rantwijk/Galil intellectual lineage with NetworkX.
// Separate JavaScript runtime + independently audited certificate, NOT independent theorem.
import { createRequire } from 'node:module';
import { candidateEdges } from './matching.ts';
const require = createRequire(import.meta.url);
const blossom = require('../../vendor/blossom_with_state.cjs');
export { candidateEdges };

const SCALE = 4503599627370496; // 2^52, exactly representable in JS
const STOP = (reason) => { throw new Error(reason); };
const guard = (test, reason) => { if (!test) STOP(reason); };

function canonical(pair) {
  return pair[0] < pair[1] ? pair : [pair[1], pair[0]];
}
function pairKey(a,b) {return a < b ? `${a},${b}` : `${b},${a}`;}
function leaves(b, s, depth = 0) {
  guard(depth <= 2*s.nVertex+2, 'INVALID_DUAL_BLOSSOM_RECURSION');
  if (b < s.nVertex) return [b];
  return s.blossomChilds[b].flatMap(c => leaves(c,s,depth+1));
}

// Certifies the weighted matching via weak duality + complementary slackness.
// All quantities are exact safe integers, except the initial binary64 weights.
export function verifyDual(s, weights, pairs, upperBound) {
  const n = s.nVertex;
  guard(Array.isArray(s.dualVar) && s.dualVar.length === 2*n, 'INVALID_DUAL_SHAPE');
  guard(n === 0 || s.blossomParent.length === 2*n, 'INVALID_BLOSSOM_SHAPE');
  const matched = new Map();
  for (const [a,b] of pairs) {
    guard(a!==b && !matched.has(a) && !matched.has(b), 'INVALID_MATCHING_VERTEX_REPEAT');
    const k=pairKey(a,b);
    guard(weights.has(k), 'INVALID_MATCH_EDGE_NOT_IN_GRAPH');
    matched.set(a,b);matched.set(b,a);
  }
  const activeBlossoms=[];
  for (let b=n;b<2*n;b++) {
    if (s.blossomBase[b]===undefined || s.blossomBase[b]<0) continue;
    const z=s.dualVar[b];
    guard(Number.isSafeInteger(z) && z>=0, 'DUAL_INVALID_BLOSSOM_VALUE');
    const vs=leaves(b,s);
    guard(vs.length>=3 && vs.length%2===1 && new Set(vs).size===vs.length, 'INVALID_ODD_BLOSSOM');
    const set=new Set(vs);let used=0;
    for(const v of vs)if(matched.has(v)&&set.has(matched.get(v))&&v<matched.get(v))used++;
    if(z>0)guard(used===Math.floor(vs.length/2),'DUAL_BLOSSOM_NOT_SATURATED');
    activeBlossoms.push({b,z,vertices:vs,matched_inside:used});
  }
  function ancestorBlossoms(v) {
    const a=[];let p=s.blossomParent[v],iteration=0;
    while(p>=0){
      guard(++iteration<=2*n, 'INVALID_PARENT_LOOP');
      guard(p>=n && p<2*n,'INVALID_BLOSSOM_PARENT');
      a.push(p); p=s.blossomParent[p];
    }
    return new Set(a);
  }
  const ancestors=Array.from({length:n},(_,v)=>ancestorBlossoms(v));
  for(let v=0;v<n;v++){
    const y=s.dualVar[v];
    guard(Number.isSafeInteger(y) && y>=0,'DUAL_INVALID_VERTEX_VALUE');
    if(!matched.has(v))guard(y===0,'DUAL_UNMATCHED_POSITIVE');
  }
  let minSlack=Infinity,tightUnused=0,edgeChecks=0;
  for (const [key,wt] of weights) {
    const [a,b]=key.split(',').map(Number);
    guard(a<n && b<n, 'DUAL_VERTEX_OUTSIDE_GRAPH');
    let twiceSlack=s.dualVar[a]+s.dualVar[b]-2*wt;
    for(const [bl,zb] of activeBlossoms.map(x=>[x.b,x.z]))
      if(ancestors[a].has(bl) && ancestors[b].has(bl))twiceSlack+=2*zb;
    guard(Number.isSafeInteger(twiceSlack),'DUAL_SLACK_UNSAFE_INTEGER');
    if(twiceSlack<0)STOP(`DUAL_NEGATIVE_EDGE_SLACK:${key}:${twiceSlack}`);
    if(matched.get(a)===b)guard(twiceSlack===0,`DUAL_MATCHED_EDGE_NOT_TIGHT:${key}`);
    else if(twiceSlack===0)tightUnused++;
    minSlack=Math.min(minSlack,twiceSlack);edgeChecks++;
  }
  let primal=0,dual2=0;
  for(const [a,b] of pairs)primal+=weights.get(pairKey(a,b));
  for(let v=0;v<n;v++)dual2+=s.dualVar[v];
  for(const x of activeBlossoms)dual2+=2*x.z*Math.floor(x.vertices.length/2);
  guard(Number.isSafeInteger(primal*2)&&Number.isSafeInteger(dual2),'DUAL_OBJECTIVE_UNSAFE');
  guard(dual2===2*primal,`PRIMAL_DUAL_GAP:${dual2-2*primal}`);
  guard(primal<=upperBound,'EXACT_OBJECTIVE_UPPER_BOUND_EXCEEDED');
  return { certificate_type:'INTEGER_PRIMAL_DUAL_COMPLEMENTARY_SLACKNESS',
    certified:true,objective2:2*primal,dual_objective2:dual2,
    checked_edges:edgeChecks,active_blossoms:activeBlossoms.length,
    positive_blossoms:activeBlossoms.filter(x=>x.z>0).length,
    tight_unselected_edges:tightUnused,min_slack2:Number.isFinite(minSlack)?minSlack:null,
    unique_proven:tightUnused===0,raw_dual:{n,dual:s.dualVar,
      parent:s.blossomParent,base:s.blossomBase,childs:s.blossomChilds}};
}

export function matching(nodes, graph, limits={}) {
  const allowed=new Set(nodes);
  guard(allowed.size===nodes.length && nodes.every(x=>Number.isSafeInteger(x)&&x>=0),'INVALID_NODES');
  const limitEdges=limits.maxEdges??12000, maxWallMs=limits.maxWallMs??5000;
  guard(graph.length<=limitEdges,'MATCH_RESOURCE_LIMIT:EDGES');
  const start=performance.now();
  const weights=new Map(), residuals=[];
  for(const e of graph){
    const [a,b]=e.pair;
    guard(a!==b && allowed.has(a)&&allowed.has(b),'INVALID_MATCH_EDGE');
    guard(Number.isFinite(e.weight)&&e.weight>=1 && e.weight<1.000101,'INVALID_MATCH_WEIGHT');
    const u=(e.weight-1)*SCALE;
    guard(Number.isSafeInteger(u)&&u>=0,'UNSAFE_BINARY64_RESIDUAL');
    const k=pairKey(a,b);
    guard(!weights.has(k),'DUPLICATE_EDGE');
    weights.set(k,u);residuals.push([a,b,u]);
  }
  if(graph.length===0)return {pairs:[],cardinality:0,unique:true,
    status:'UNIQUE_EMPTY_OPTIMUM',certified_optimality:true,
    exact_weight_residue:0,full_units_in_2_power_minus52:'0',
    full_units_schema_version:2,full_units_format:'decimal_bigint_string',
    proof:'EMPTY_GRAPH',certificate:{certificate_type:'EMPTY_GRAPH',certified:true},
    uniqueness_status:'PROVED_UNIQUE'};
  const cardinalBound=Math.floor(nodes.length/2),maxDelta=Math.max(...residuals.map(x=>x[2]));
  const BASE=cardinalBound*maxDelta+1;
  guard(Number.isSafeInteger(BASE),'MATCH_BASE_UNSAFE');
  const transformed=residuals.map(([a,b,r])=>[a,b,BASE+r]);
  guard(cardinalBound*(BASE+maxDelta)<Number.MAX_SAFE_INTEGER/2,'MATCH_SUM_UNSAFE');
  const transformedWeights=new Map(transformed.map(([a,b,w])=>[pairKey(a,b),w]));
  const state=blossom.withState(transformed);
  const mate=state.mate,pairs=[];
  for(let a=0;a<mate.length;a++)if(mate[a]>=0 && a<mate[a])pairs.push([a,mate[a]]);
  pairs.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  const cert=verifyDual(state,transformedWeights,pairs,cardinalBound*(BASE+maxDelta));
  guard(performance.now()-start<=maxWallMs,`MATCH_RESOURCE_LIMIT:WALL:${maxWallMs}`);
  const residual=pairs.reduce((s,[a,b])=>s+weights.get(pairKey(a,b)),0);
  guard(Number.isSafeInteger(residual),'UNSAFE_MATCH_RESIDUAL_SUM');
  // The whole scaled objective is often > 2^53-1 even for 2+ selected edges.
  // Never perform this sum in Number; serialize the exact integer as a string.
  const fullUnits=(BigInt(pairs.length)*(1n<<52n)+BigInt(residual)).toString();
  const {raw_dual,...compactCert}=cert;
  return {pairs,cardinality:pairs.length,unique:cert.unique_proven,
    uniqueness_status:cert.unique_proven?'PROVED_UNIQUE_BY_STRICT_SLACK':'NOT_CERTIFIED',
    status:cert.unique_proven?'UNIQUE_PRIMAL_DUAL_CERTIFICATE':'OPTIMAL_PAIR_SELECTED_UNIQUENESS_UNVERIFIED',
    certified_optimality:true,exact_weight_residue:residual,
    full_units_in_2_power_minus52:fullUnits,
    full_units_schema_version:2,full_units_format:'decimal_bigint_string',
    proof:'MIT_JS_BLOSSOM_INTEGER_PRIMAL_DUAL_CERT',
    certificate:compactCert,baseline_integer:BASE,
    ...(limits.emitWitness ? {dual_witness:raw_dual} : {}),
    backend:'mattkrick_2015_MIT_Galil_Joris_lineage',
    elapsed_ms:Math.round((performance.now()-start)*1000)/1000};
}
