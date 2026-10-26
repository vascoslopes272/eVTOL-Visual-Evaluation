"""Agreement and 95 % intervals for the domain resample, from the two exported decision files
(review/decisions/DOMAIN_RESAMPLE_{IN,OUT}_DECISIONS.csv). Run after the author has judged all 163.
Per side: k/n with the Wilson interval with finite-population correction (pools 871 and 358).
Pooled: stratified estimate of the script's overall accuracy on the 1 229 pages,
(871 p_in + 358 p_out)/1229, with the stratified normal interval (fpc per stratum), because the two sides are
sampled at different fractions (87/871 vs 76/358); the plain Wilson on 163 of 1 229 is printed beside it."""
import math, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(HERE))
from lib import intervals
D = HERE / "review" / "decisions"
rows = []; strata = []
for side, f, N, right in [("kept in the domain (871)", "DOMAIN_RESAMPLE_IN_DECISIONS.csv", 871, "in_domain"),
                          ("deleted as out of domain (358)", "DOMAIN_RESAMPLE_OUT_DECISIONS.csv", 358, "exclude")]:
    d = pd.read_csv(D / f, keep_default_na=False); n = len(d); k = int((d.decision == right).sum())
    lo, hi = intervals.wilson_fpc_interval(k, n, N); strata.append((N, n, k))
    rows.append((side, k, n, N, k / n, lo, hi))
    print(f"{side}: {k}/{n} = {100*k/n:.1f} %  95 % {100*lo:.1f}-{100*hi:.1f}  | est. wrong pages {round(N*(1-k/n))} ({round(N*(1-hi))}-{round(N*(1-lo))})")
Nt = sum(s[0] for s in strata); p = sum(N * k / n for N, n, k in strata) / Nt
var = sum((N / Nt) ** 2 * (1 - n / N) * (k / n) * (1 - k / n) / (n - 1) for N, n, k in strata)
se = math.sqrt(var)
print(f"two sides together (stratified): {100*p:.1f} %  95 % {100*(p-1.96*se):.1f}-{100*min(1,p+1.96*se):.1f}  (n = {sum(s[1] for s in strata)}, pool {Nt})")
K = sum(s[2] for s in strata); Nn = sum(s[1] for s in strata); lo, hi = intervals.wilson_fpc_interval(K, Nn, Nt)
print(f"plain Wilson on the pooled counts: {K}/{Nn} = {100*K/Nn:.1f} %  95 % {100*lo:.1f}-{100*hi:.1f}  (ignores unequal sampling fractions)")
