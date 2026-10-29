"use strict";
// N85. Frozen BEFORE executing results. No human data. This is NOT original ESBM Python execution.
// A source guard ensures the tested failure mode exists in the exact pinned ESBM v2 source.
function auditN85(pythonSource) {
 const checks={
  original_function:pythonSource.includes("def simulate(seed, name, config):"),
  completed_only:pythonSource.includes("'duration_completed_mean':float(np.mean(completed_duration)) if completed_duration else None"),
  censored_computed:pythonSource.includes("censored_durations=[STEPS-int(start[i]) for i in range(N) if partner[i]>i]"),
  only_censored_count_persisted:pythonSource.includes("'right_censored_count':len(censored_durations)"),
  ended_at_start_tick:pythonSource.includes("duration=t-int(start[i]); completed_duration.append(duration)"),
  horizon_16:pythonSource.includes("N=144; STEPS=16; K=7"),
  exogenous_hazard:pythonSource.includes("h=min(.90, (.12+.065*(norm[i]!=norm[j])+.004*abs(int(age[i])-int(age[j])))*config['hazard_mult'])")
 };
 if(Object.values(checks).some(v=>!v))throw Error("FROZEN_SOURCE_ASSUMPTION_FAILED:"+JSON.stringify(checks));
 const hs=[{name:"longer_partnerships_base_only",h:0.048},{name:"mixed_random_base_only",h:0.12},{name:"shorter_partnerships_base_only",h:0.21}];
 const n=50000,T=16;
 let randState=0x72a6e119;
 function random(){randState^=randState<<13;randState^=randState>>>17;randState^=randState<<5;return (randState>>>0)/4294967296;}
 const results=[];
 for(const scenario of hs){
  const h=scenario.h,q=1-h,events=Array(T+1).fill(0);let completed=0,rawSum=0,censored=0;
  for(let i=0;i<n;i++){
   let ended=false;
   for(let t=1;t<T;t++){
    if(random()<h){events[t]++;completed++;rawSum+=t;ended=true;break;}
   }
   if(!ended){censored++;}
  }
  const naive=rawSum/completed;
  let risk=n,survival=1,rmst=0;
  for(let t=0;t<T;t++){
   rmst+=survival;
   if(t>=1){ // event at t changes the curve only from t onwards, not before
    // adjustment is deliberately delayed to next iteration by this placement:
   }
   if(t+1<T){survival*=1-events[t+1]/risk;risk-=events[t+1];}
  }
  const analyticRMST=(1-Math.pow(q,T))/h;
  const analyticCompletedNumerator=Array.from({length:T-1},(_,i)=>(i+1)*h*Math.pow(q,i)).reduce((a,b)=>a+b,0);
  const analyticCompletedMean=analyticCompletedNumerator/(1-Math.pow(q,T-1));
  const calcCheck=Math.abs(rmst-analyticRMST)<0.17 && Math.abs(naive-analyticCompletedMean)<0.18;
  const strictGap=rmst-naive>0.20;
  const conserved=completed+censored===n&&events.slice(1).reduce((a,b)=>a+b,0)===completed;
  results.push({name:scenario.name,h,cohorts:n,horizon:T,completed,censored,
   naive_completed_mean:naive,km_restricted_mean_16:rmst,known_true_restricted_mean_16:analyticRMST,
   analytic_completed_only_mean:analyticCompletedMean,
   km_minus_naive:rmst-naive,completes:calcCheck&&strictGap&&conserved,
   test:{analytic_within_tolerance:calcCheck,restricted_beats_completed:strictGap,cohort_balance:conserved}});
 }
 if(results.some(x=>!x.completes))throw Error("PRECOMMITTED_SURVIVAL_TEST_FAILED:"+JSON.stringify(results));
 return {status:"FORMAL_SYNTHETIC_CENSORING_DIAGNOSTIC_NOT_ESBM_PYTHON_EXECUTION",code_source_guards:checks,
 model:"all relationships enter at tick zero, known constant hazard per tick, dissolution tried ticks 1–15, administrative censor at 16",
 independent_human_holdout:false,original_human_rows:0,settings:{replicates_per_hazard:n,seed_hex:"72a6e119",horizon:T,hazards:hs.map(x=>x.h),tolerance_km_rmst:0.17,tolerance_completed_mean:0.18},
 results,claim:"Source's completed-only duration mean is not a consistent unrestricted/16-tick restricted mean when censored pairs remain; bias changes with hazard. Fix requires retaining individual durations+event flags and calculating KM/RMST, not reading completed mean as population average."};
}
