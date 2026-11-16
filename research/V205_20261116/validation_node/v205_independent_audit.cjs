/* Exact independent-language enumeration; no Python game/gradient imports. */
const fs=require('fs'),path=require('path');
const base=path.resolve(__dirname,'..'),folder=path.join(base,'results','V205_ADVALIGN_NASH_AUDIT');
const output=path.join(base,'results','V205_NODE_INDEPENDENT_AUDIT.json');
if(fs.existsSync(output))throw Error('Preserve existing audit');
function sigmoid(x){return 1/(1+Math.exp(-x));}
function bit(x,k){return (x>>>k)&1;}
function zeros(){return [[0,0,0],[0,0,0]];}
function field(gamma,beta,c,variant,kind,lambda){
 const g=zeros();
 for(let m=0;m<16;m++){
  const a0=bit(m,0),b0=bit(m,1),a1=bit(m,2),b1=bit(m,3);
  const z=2*b0-1,x=2*a0-1,f=2*a1-1,h=2*b1-1,s=b0?1:2;
  const A=[[z*(1+c*x),c*f*h],[-c*x*z,f*(z-c*h)]];
  if(kind==='marginal')for(let i=0;i<2;i++)A[i]=[0,0];
  else if(kind==='gae')for(let i=0;i<2;i++)A[i][0]+=gamma*lambda*A[i][1];
  const acts=[[a0,a1],[b0,b1]];
  for(let i=0;i<2;i++){
   g[i][0]+=A[i][0]*(acts[i][0]-.5)/16;
   let extra;
   if(variant==='eq8')extra=gamma**3*A[i][0]*A[1-i][1];
   else extra=.5*A[i][0]*A[1-i][1];
   g[i][s]+=(gamma*A[i][1]+beta*extra)*(acts[i][1]-.5)/16;
  }
 }
 return g;
}
function returns(p,gamma,c){
 const v=[0,0];
 for(let m=0;m<16;m++){
  const a0=bit(m,0),b0=bit(m,1),a1=bit(m,2),b1=bit(m,3),s=b0?1:2;
  let pr=1;
  for(const [i,h,a] of [[0,0,a0],[1,0,b0],[0,s,a1],[1,s,b1]])pr*=a?p[i][h]:1-p[i][h];
  const z=2*b0-1,x=2*a0-1,f=2*a1-1,h=2*b1-1;
  v[0]+=pr*(z*(1+c*x)+gamma*c*f*h);
  v[1]+=pr*(-c*x*z+gamma*f*(z-c*h));
 }
 return v;
}
function br(p,gamma,c){
 const v=returns(p,gamma,c),max=[-Infinity,-Infinity];
 for(let i=0;i<2;i++)for(let k=0;k<8;k++){
  const changed=p.map(r=>[...r]);changed[i]=[bit(k,0),bit(k,1),bit(k,2)];
  max[i]=Math.max(max[i],returns(changed,gamma,c)[i]);
 }
 return {v,gains:max.map((x,i)=>x-v[i])};
}
let maxFieldError=0,maxBRError=0,literalChecks=0,sourceChecks=0;
const records=[];
const rows=JSON.parse(fs.readFileSync(path.join(folder,'LITERAL_FIELDS.json'),'utf8'));
for(const r of rows){
 const actual=field(r.gamma,r.beta,r.coupling,r.variant,r.advantages,r.lmbda);
 for(let i=0;i<2;i++)for(let h=0;h<3;h++)maxFieldError=Math.max(maxFieldError,Math.abs(actual[i][h]-r.field[i][h]));
 const result=br(actual.map(row=>row.map(x=>sigmoid(.1*x))),r.gamma,r.coupling);
 for(let i=0;i<2;i++)maxBRError=Math.max(maxBRError,Math.abs(result.gains[i]-r.after_step.gains[i]),Math.abs(result.v[i]-r.after_step.values[i]));
 const initial=br([[.5,.5,.5],[.5,.5,.5]],r.gamma,r.coupling);
 if(Math.max(...initial.gains.map(Math.abs))>1e-12)throw Error('Initial profile not Nash');
 literalChecks++;
}
const source=JSON.parse(fs.readFileSync(path.join(folder,'AUTHOR_HELPERS.json'),'utf8'));
for(const r of source){
 const result=br(r.gradient.map(row=>row.map(x=>sigmoid(.1*x))),.9,r.coupling);
 for(let i=0;i<2;i++)maxBRError=Math.max(maxBRError,Math.abs(result.gains[i]-r.after_step.gains[i]),Math.abs(result.v[i]-r.after_step.values[i]));
 sourceChecks++;
}
if(maxFieldError>1e-10||maxBRError>1e-10)throw Error('Cross-language discrepancy');
const result={status:'PASS',literalProfiles:literalChecks,originalSourcePostStepProfiles:sourceChecks,
 maxFieldError,maxBestResponseError:maxBRError,
 independentImplementation:true,externalScientificConfirmation:false,
 method:'Literal JavaScript action enumeration, score products and exhaustive 8-policy unilateral deviations'};
fs.writeFileSync(output,JSON.stringify(result,null,2));process.stdout.write(JSON.stringify(result)+'\n');
