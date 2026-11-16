"""Independent exact-symbolic certificate; no simulator or upstream imports."""
from pathlib import Path
import hashlib
import itertools
import json
import sympy as s

B=Path(__file__).resolve().parent


def main():
    gamma,beta,alpha=s.symbols('gamma beta alpha',positive=True)
    c=s.symbols('c',nonnegative=True)
    field=s.zeros(2,3);own=s.zeros(2,3)
    for a0,b0,a1,b1 in itertools.product([0,1],repeat=4):
        x=2*a0-1;z=2*b0-1;f=2*a1-1;g=2*b1-1;h=1 if b0 else 2
        a=[[z*(1+c*x),c*f*g],[-c*x*z,f*(z-c*g)]]
        actions=[[a0,a1],[b0,b1]]
        for i in range(2):
            own[i,0]+=s.Rational(1,16)*a[i][0]*(actions[i][0]-s.Rational(1,2))
            own[i,h]+=s.Rational(1,16)*gamma*a[i][1]*(actions[i][1]-s.Rational(1,2))
            field[i,h]+=s.Rational(1,16)*beta*gamma**3*a[i][0]*a[1-i][1]*(actions[i][1]-s.Rational(1,2))
    field=field.applyfunc(s.simplify);own=own.applyfunc(s.simplify)
    expected=s.zeros(2,3);expected[0,1]=expected[0,2]=beta*gamma**3/4
    assert field==expected and own==s.zeros(2,3)
    initial_unilateral_values=[]
    for focal in range(2):
        for policy in itertools.product([0,1],repeat=3):
            value=0
            for a0,b0,a1,b1 in itertools.product([0,1],repeat=4):
                h=1 if b0 else 2;actions=[[a0,a1],[b0,b1]]
                if actions[focal][0]!=policy[0] or actions[focal][1]!=policy[h]:continue
                x=2*a0-1;z=2*b0-1;f=2*a1-1;g=2*b1-1
                ret=[z*(1+c*x)+gamma*c*f*g,-c*x*z+gamma*f*(z-c*g)]
                value+=s.Rational(1,4)*ret[focal]
            value=s.simplify(value);assert value==0
            initial_unilateral_values.append(str(value))
    p=s.symbols('p10 p20 p1p p2p p1m p2m')
    p10,p20,p1p,p2p,p1m,p2m=p
    v2p=(2*p1p-1)*(1-c*(2*p2p-1))
    v2m=(2*p1m-1)*(-1-c*(2*p2m-1))
    eq=s.Matrix([2*c*(2*p20-1),-2*c*(2*p10-1)+gamma*(v2p-v2m),
        2*c*(2*p2p-1),-2*c*(2*p1p-1),2*c*(2*p2m-1),-2*c*(2*p1m-1)])
    at={x:s.Rational(1,2) for x in p}
    assert eq.subs(at)==s.zeros(6,1)
    determinant=s.factor(eq.jacobian(p).subs(at).det())
    assert determinant==4096*c**6
    regret=gamma*(1+c)*s.tanh(alpha*beta*gamma**3/8)
    assert regret.is_positive
    # Marginal-vs-joint discrepancy is exact even with perfect value functions.
    result=dict(study='V205',status='PASS',method='SymPy exact symbolic action enumeration, unilateral policies and equilibrium-condition Jacobian',
        own_gradient=[[str(own[i,j]) for j in range(3)] for i in range(2)],
        AA_correction=[[str(field[i,j]) for j in range(3)] for i in range(2)],
        pure_unilateral_policy_certificates=16,all_initial_unilateral_values=initial_unilateral_values,
        marginal_Nash_conditions_zero=True,isolated_equilibrium_jacobian_determinant=str(determinant),
        isolated_for_positive_c=True,exact_player2_regret_after_joint_advantage_step=str(regret),
        regret_positive_for_positive_gamma_beta_alpha=True,
        general_learning_success_or_welfare_claim=False,external_scientific_confirmation=False,
        sympy_version=s.__version__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out=B/'results/V205_SYMBOLIC_CERTIFICATE.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
