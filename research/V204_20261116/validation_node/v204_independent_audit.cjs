/* Independent-language literal-enumeration audit, post hoc.
   Reuses the previously audited JS physics; never calls Python operators. */
const fs=require('fs'),path=require('path');
const base=path.resolve(__dirname,'..');
const output=path.join(base,'results','V204_NODE_INDEPENDENT_AUDIT.json');
if(fs.existsSync(output))throw Error('Preserve earlier output');
const stock=.8903152454708944, f=1-Math.exp(-stock),y=.25*f,aut=y-.05,beta=.95;
function bit(mask,i){return (mask>>>i)&1;}
function observation(h,i,s,pub){
 const mask=Math.floor(h/3);
 let n=0;
 if(mask===8)n=4;
 else if(pub||i===3){for(let j=0;j<3;j++)n+=bit(mask,j);}
 else n=bit(mask,i);
 return 2*(3*n+h%3)+s;
}
function outcomes(p,loss,pub,h,override=null,noPay=false){
 const P=new Float64Array(27),R=new Float64Array(4);let G=0;
 const focal=override===null?-1:override.i;
 for(let good=0;good<2;good++){
  const prior=override===null?(good?.65:.35):(good?(override.s?52/59:13/41):(override.s?7/59:28/41));
  for(let sig=0;sig<16;sig++){
   if(focal>=0&&bit(sig,focal)!==override.s)continue;
   let signalProb=prior;
   for(let i=0;i<4;i++)if(i!==focal)signalProb*=bit(sig,i)?(good?.8:.2):(good?.2:.8);
   for(let modes=0;modes<16;modes++){
    if(focal>=0&&bit(modes,focal)!==override.mode)continue;
    let modeProb=signalProb;
    for(let i=0;i<4;i++)if(i!==focal){
     const v=p[i][observation(h,i,bit(sig,i),pub)][0];
     modeProb*=bit(modes,i)?v:1-v;
    }
    if(modeProb===0)continue;
    const complete=modes===15;
    const goodJoint=complete&&good;
    for(let paymask=0;paymask<(goodJoint&&!noPay?8:1);paymask++){
     if(goodJoint&&!noPay&&focal>=0&&focal<3&&bit(paymask,focal)!==override.pay)continue;
     let probability=modeProb;
     if(goodJoint&&!noPay)for(let i=0;i<3;i++)if(i!==focal){
      const v=p[i][observation(h,i,bit(sig,i),pub)][1];
      probability*=bit(paymask,i)?v:1-v;
     }
     if(probability===0)continue;
     let next;
     if(goodJoint)next=paymask*3+2;
     else next=Math.floor(h/3)*3+(complete&&!good?1:0);
     P[next]+=probability;if(goodJoint)G+=probability;
     for(let i=0;i<4;i++){
      let r=complete?(good?y+.8*f-.05:-loss[i]-.05):aut;
      if(i===3){
       if(bit(modes,3))r-=.30;
       if(goodJoint)for(let j=0;j<3;j++)r+=.25*bit(paymask,j);
      }else if(goodJoint)r-=.25*bit(paymask,i);
      R[i]+=probability*r;
     }
    }
   }
  }
 }
 const sum=P.reduce((a,b)=>a+b,0);
 if(Math.abs(sum-1)>1e-11)throw Error('Transition row does not sum to one: '+sum);
 return {P,R,G};
}
function discounted(rows,k){
 let v=new Float64Array(27),residual=Infinity,iterations=0;
 for(;iterations<2000;iterations++){
  const next=new Float64Array(27);residual=0;
  for(let h=0;h<27;h++){
   let x=k===4?rows[h].G:rows[h].R[k];
   for(let j=0;j<27;j++)x+=beta*rows[h].P[j]*v[j];
   next[h]=x;residual=Math.max(residual,Math.abs(x-v[h]));
  }
  v=next;if(residual<1e-12)break;
 }
 if(iterations>=2000)throw Error('Value iteration did not converge');
 return {v,residual,iterations};
}
function evaluate(p,loss,pub){
 const rows=Array.from({length:27},(_,h)=>outcomes(p,loss,pub,h));
 const disabled=Array.from({length:27},(_,h)=>outcomes(p,loss,pub,h,null,true));
 const values=Array.from({length:4},(_,i)=>discounted(rows,i));
 const good=discounted(rows,4),noPay=discounted(disabled,4);
 return {returns:values.map(x=>.05*x.v[24]),good:.05*good.v[24],
  disabled:.05*noPay.v[24],values,rows,
  maximumResidual:Math.max(...values.map(x=>x.residual),good.residual,noPay.residual)};
}
function bestResponse(p,loss,i){
 const rows=Array.from({length:27},(_,h)=>[0,1].map(s=>[
  outcomes(p,loss,true,h,{i,s,mode:0,pay:0}),
  outcomes(p,loss,true,h,{i,s,mode:1,pay:0}),
  outcomes(p,loss,true,h,{i,s,mode:1,pay:1})]));
 let v=new Float64Array(27),residual=Infinity,iteration=0;
 for(;iteration<2000;iteration++){
  const next=new Float64Array(27);residual=0;
  for(let h=0;h<27;h++)for(let s=0;s<2;s++){
   let best=-Infinity;
   for(const row of rows[h][s]){
    let q=row.R[i];for(let j=0;j<27;j++)q+=beta*row.P[j]*v[j];
    best=Math.max(best,q);
   }
   next[h]+=(s?.59:.41)*best;
  }
  for(let h=0;h<27;h++)residual=Math.max(residual,Math.abs(next[h]-v[h]));
  v=next;if(residual<1e-12)break;
 }
 if(iteration>=2000)throw Error('Best-response value iteration failed');
 return {value:v[24],residual,iteration};
}

const input=JSON.parse(fs.readFileSync(path.join(base,'results','V204_NODE_INPUT.json'),'utf8'));
let maxNativeError=0,maxBehaviorError=0,maxBRerror=0,cases=0,brChecks=0;
const checked=[];
for(const rec of input.records){
 const p=rec.logits.map(player=>player.flatMap(h=>h.map(heads=>heads.map(v=>1/(1+Math.exp(-Math.max(-12,Math.min(12,v))))))));
 const own=evaluate(p,input.losses,true), e=rec.expected.native_evaluation;
 let error=Math.max(Math.abs(own.good-e.discounted_GOOD_joint_rate),Math.abs(own.disabled-e.disabled_payment_GOOD_rate));
 for(let i=0;i<4;i++)error=Math.max(error,Math.abs(own.returns[i]-e.normalized_private_return[i]));
 const functional=Math.min(...own.returns.map(x=>x-aut))>=.02&&own.good>=.20&&own.good-own.disabled>=.10;
 if(error>1e-9||functional!==e.functional)throw Error('Native mismatch '+rec.case+'/'+rec.time+'/'+error);
 maxNativeError=Math.max(maxNativeError,error);
 const eps=.20-.18*Math.min(rec.time/48,1);
 const mixed=p.map(player=>player.map(heads=>heads.map(v=>eps/2+(1-eps)*v)));
 const behavior=evaluate(mixed,input.losses,true);
 for(let i=0;i<4;i++)maxBehaviorError=Math.max(maxBehaviorError,Math.abs(behavior.returns[i]-rec.expected.behavior_normalized_private_return[i]));
 if(maxBehaviorError>1e-9)throw Error('Behavior value mismatch');
 if(rec.check_best_response)for(let i=0;i<4;i++){
  const br=bestResponse(p,input.losses,i);
  const err=Math.abs(.05*br.value-own.returns[i]-rec.expected.public_deviations.normalized_gain_per_agent[i]);
  if(err>1e-8)throw Error('BR mismatch '+rec.case+'/'+i+'/'+err);
  maxBRerror=Math.max(maxBRerror,err);brChecks++;
 }
 cases++;checked.push({case:rec.case,time:rec.time,error,functional});
}
const result={status:'PASS',cases,scalar_native_checks:6*cases,scalar_behavior_checks:4*cases,
 public_best_response_checks:brChecks,maxNativeError,maxBehaviorError,maxBRerror,
 method:'Independent JavaScript literal enumeration and value iteration; native sigmoid independently reconstructed from logits',
 external_scientific_confirmation:false,checked};
fs.writeFileSync(output,JSON.stringify(result,null,2));
process.stdout.write(JSON.stringify({...result,checked:undefined})+'\n');
