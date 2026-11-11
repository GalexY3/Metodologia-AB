"""Tiny exact numerical counterexamples / checks to assertions in Argon brief."""
import math,unittest,random
from fractions import Fraction

def food(n,N,k):
    if n==0:return 0.
    q=N/k
    return min(n/q,q/n)
def potential(counts,N,k):
    return sum(sum(food(t,N,k) for t in range(1,n+1)) for n in counts)
def gain(s,a,b,N,k):
    return food(s[b]+1,N,k)-food(s[a],N,k)
def candidate(counts,a,b):
    ans=list(counts)
    ans[a]-=1;ans[b]+=1
    return ans

class FormalChecks(unittest.TestCase):
    def test_rosenthal_exact_potential_all_one_player_deviations(self):
        rng=random.Random(20261111)
        for N,k,M in ((12,10,12),(18,3,10),(120,4,12),(120,60,80)):
            for _ in range(20):
                counts=[0]*M
                for _ in range(N):counts[rng.randrange(M)]+=1
                active=[j for j,n in enumerate(counts) if n]
                for _ in range(20):
                    a=rng.choice(active)
                    b=rng.randrange(M)
                    if a==b:continue
                    dphi=potential(candidate(counts,a,b),N,k)-potential(counts,N,k)
                    self.assertAlmostEqual(dphi,gain(counts,a,b,N,k),places=10)
    def test_overfragmented_noninteger_can_be_strict_nash(self):
        N=12;k=10;count=[1]*12
        self.assertGreater(sum(bool(x) for x in count),k)
        margins=[gain(count,i,j,N,k) for i in range(12) for j in range(12) if i!=j]
        self.assertLess(max(margins),0)
    def test_bottleneck_founder_tie_vs_strict(self):
        N=120;k=4;q=N/k;old=60
        self.assertEqual(food(old,N,k),food(15,N,k))
        self.assertGreater(food(16,N,k),food(old,N,k))
        self.assertLess(food(14,N,k),food(old,N,k))
    def test_p_leave_is_expectation_not_exact_state(self):
        p=1-food(60,120,4)
        self.assertEqual(60*(1-p),30)
        self.assertAlmostEqual(math.comb(60,30)*(.5**60),0.10257817300856951,places=14)
    def test_u1_has_120_group_optimum_when_k80_if_M120(self):
        N,k,M=120,80,120
        lo=math.floor(N/k);hi=math.ceil(N/k)
        u=lambda n:min(1,n/lo,hi/n)
        balanced=[1]*40+[2]*40
        overfragmented=[1]*120
        self.assertEqual(sum(balanced),N)
        self.assertEqual(sum(overfragmented),N)
        self.assertEqual(sum(n*u(n) for n in balanced),N)
        self.assertEqual(sum(n*u(n) for n in overfragmented),N)
    def test_fractional_pigou_proposal_not_marginal_of_food(self):
        N,k=120,7;q=Fraction(N,k)
        F=lambda n:Fraction(n*n,1)/q if n<=q else q
        marginal17=F(17)-F(16)
        marginal18=F(18)-F(17)
        self.assertLess(float(marginal18/marginal17),.15)
        argon18=1
        self.assertNotAlmostEqual(float(marginal18/marginal17),argon18,places=5)
    def test_binomial_fano_is_not_necessary_for_independent_heterogeneity(self):
        # Independent Bernoulli decisions with heterogeneous private rates:
        # half leave deterministically, half never. Fano = 0, yet no
        # covariance across agents, no messages, no collective coordination.
        ps=[1]*30+[0]*30
        mean=sum(ps);var=sum(p*(1-p) for p in ps)
        self.assertEqual(var/mean,0)
if __name__=='__main__':unittest.main(verbosity=2)
