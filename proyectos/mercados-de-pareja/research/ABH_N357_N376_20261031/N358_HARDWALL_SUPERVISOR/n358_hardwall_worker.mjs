// AB-H N358: isolated worker with adversarial probes restricted to test harness.
// Never import/modify the historical ESBM Python simulator.
import {matching} from '../work/src/blossom_matching.mjs';
let text='';
for await(const chunk of process.stdin){
 text+=chunk;
 if(Buffer.byteLength(text)>1048576)throw new Error('INPUT_TOO_LARGE');
}
const request=JSON.parse(text);
if(request.mode==='stall'){
 const until=performance.now()+2000;
 while(performance.now()<until){} // Intentional adversarial infinite-ish worker delay.
 console.log(JSON.stringify({status:'INVALID_TEST_COMPLETION'}));
}else if(request.mode==='corrupt_json'){
 console.log('this is not json');
}else if(request.mode==='crash'){
 throw new Error('INJECTED_WORKER_CRASH');
}else if(request.mode==='large_output'){
 process.stdout.write('x'.repeat(600000));
}else if(request.mode==='matching'){
 const nodes=request.nodes, edges=request.edges;
 if(!Array.isArray(nodes)||!Array.isArray(edges))throw new Error('INVALID_INPUT');
 const answer=matching(nodes,edges,{maxWallMs:request.softWallMs??30000});
 console.log(JSON.stringify({status:'MATCHING_COMPLETED',answer}));
}else{
 throw new Error('INVALID_MODE');
}
