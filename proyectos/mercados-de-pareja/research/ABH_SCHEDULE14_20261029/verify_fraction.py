"""Post-outcome independent rational audit of the 2x2 schedule model.
Python stdlib Fraction; NOT a preregistered confirmatory replication.
No human data, no access to external sources.
"""
from fractions import Fraction as F
from itertools import combinations

SCHEDULES = {
    "rotation": (9, 6),
    "adjacent": (3, 5, 10, 12),
    "uniform_two": tuple(sum(1 << i for i in s) for s in combinations(range(4), 2)),
}

def cardinality(consent_mask):
    edges = [(i // 2, i % 2) for i in range(4) if consent_mask & (1 << i)]
    if any(a != c and b != d for (a, b), (c, d) in combinations(edges, 2)):
        return 2
    return 1 if edges else 0

def distribution(schedule):
    out = [F(0), F(0), F(0)]
    for exposed in schedule:
        bits = [i for i in range(4) if exposed & (1 << i)]
        for k in range(len(bits) + 1):
            for subset in combinations(bits, k):
                accepted = sum(1 << i for i in subset)
                out[cardinality(accepted)] += F(1, len(schedule)) * F(1, 2) ** len(bits)
    return out

def main():
    expected = {
        "rotation": [F(1, 4), F(1, 2), F(1, 4)],
        "adjacent": [F(1, 4), F(3, 4), F(0)],
        "uniform_two": [F(1, 4), F(2, 3), F(1, 12)],
    }
    for name, schedule in SCHEDULES.items():
        observed = distribution(schedule)
        assert observed == expected[name], (name, observed)
        assert sum(observed) == 1
        mu = observed[1] + 2 * observed[2]
        print(name, "P(M=0,1,2) =", tuple(map(str, observed)), "E[M] =", mu)
    print("Post-outcome independent rational check PASS")

if __name__ == "__main__":
    main()
