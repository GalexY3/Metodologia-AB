"use strict";
// Formal AB-R N83: enumerate exact rational cell masses; no human records.
// Model A: U unobserved, P(U=1)=.5; P(E=1|U)=.2/.8.
// i accepts with probability .2/.8 by U, j with .4/.6 by U.
// Yi and Yj independent given U; no E effect on choices.
// Model B: E randomized equally; joint (Yi,Yj)|E assigned Model A's
// conditional observational distribution. Native two-person decisions retained.
// All observed E,Yi,Yj cells equal; do(E) outcomes differ.
function enumerate() {
  const numsA={},numsB={},all=[];
  const wi=[1,4],pi=[1,4],pj=[2,3];
  function num(e,yi,yj) {
    let k=0;
    for(let u=0;u<2;u++){
      const e5=e?wi[u]:5-wi[u];
      const i5=yi?pi[u]:5-pi[u];
      const j5=yj?pj[u]:5-pj[u];
      k+=e5*i5*j5;
    }
    return k; // numerator over 250
  }
  for(let e=0;e<2;e++)for(let yi=0;yi<2;yi++)for(let yj=0;yj<2;yj++){
    const key=[e,yi,yj].join("");
    numsA[key]=num(e,yi,yj);
    // P_B(E=e)=1/2, P_B(Yi,Yj|E=e)=num_A /125.
    numsB[key]=numsA[key];
    all.push({e,yi,yj,a_num_over_250:numsA[key],b_num_over_250:numsB[key]});
  }
  const sumA=all.reduce((s,x)=>s+x.a_num_over_250,0);
  const sumB=all.reduce((s,x)=>s+x.b_num_over_250,0);
  const eMass=[0,1].map(e=>all.filter(x=>x.e===e).reduce((s,x)=>s+x.a_num_over_250,0));
  const positivityP_E_by_U=[1/5,4/5];
  const maxObsDiff=Math.max(...all.map(x=>Math.abs(x.a_num_over_250-x.b_num_over_250)));
  // Model A: E has NO causal effect; under do(E) keep U marginal.
  const aDoMutual=[14/50,14/50];
  // Model B: randomized E, conditional joint data are the do distribution.
  const bDoMutual=[numsB["011"]/eMass[0],numsB["111"]/eMass[1]];
  const observationalMutual=[numsA["011"]/eMass[0],numsA["111"]/eMass[1]];
  const observedContrast=observationalMutual[1]-observationalMutual[0];
  const causalContrastA=aDoMutual[1]-aDoMutual[0];
  const causalContrastB=bDoMutual[1]-bDoMutual[0];
  const assertions={
    masses_total_A:sumA===250,masses_total_B:sumB===250,
    both_e_marginal_125:eMass.every(x=>x===125),
    observational_joint_exactly_equal:maxObsDiff===0,
    strict_positivity:positivityP_E_by_U.every(x=>x>0&&x<1),
    positive_joint_cell_counts:all.every(x=>x.a_num_over_250>0),
    observed_difference_exact:Math.abs(observedContrast-0.24)<1e-12,
    A_no_causal_effect:causalContrastA===0,
    B_nonzero_causal_effect:Math.abs(causalContrastB-0.24)<1e-12,
    observational_and_causal_disagree:Math.abs(causalContrastB-causalContrastA)>0.2
  };
  if(Object.values(assertions).some(x=>x!==true))throw Error("FORMAL_TEST_FAILED:"+JSON.stringify(assertions));
  return {
    type:"EXACT_RATIONAL_FORMAL_NON_EMPIRICAL",
    probability_denominator:250,source:"PRE-REGISTERED_AB_N83_FORMAL_IDENTIFIABILITY",
    original_human_rows_used:0,independent_sample_used:false,
    cells:all,proof_assertions:assertions,
    observed_P_mutual_given_E:observationalMutual,
    identical_observed_joint:true,
    causal_P_mutual_doE_ModelA:aDoMutual,
    causal_P_mutual_doE_ModelB:bDoMutual,
    observed_contrast:observedContrast,
    modelA_causal_effect:causalContrastA,
    modelB_causal_effect:causalContrastB,
    identification:"FAILS_EVEN_WITH_POSITIVE_P_E_GIVEN_U_AND_NATIVE_BILATERAL_YES_NO",
    conclusion:"Prediction from E and native bilateral decisions does not by itself identify the causal effect of risk-set size; unmeasured common causes can make models A and B observationally indistinguishable."
  };
}
