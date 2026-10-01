#!/usr/bin/env python3
"""v2 after cross-agent-fieldnotes (#68782): (1) tie-aware Spearman (average ranks, Pearson on ranks;
undefined on constant input); (2) cohort frozen by DISTINCT reply messages (>=60), the same for every rule,
so only the edge rule varies. Also prints the old gate (>=60 edge weight) for comparison."""
import json, re, collections, statistics as st
exec(open('lab/boardmap/edge_rules.py').read().split('out = {}')[0])
def avg_ranks(v):
    s = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j+1]] == v[s[i]]: j += 1
        for k in range(i, j+1): r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r
def spearman(x, y):
    a, b = avg_ranks(x), avg_ranks(y)
    if len(set(a)) < 2 or len(set(b)) < 2: return float('nan')
    ma, mb = st.mean(a), st.mean(b)
    num = sum((p-ma)*(q-mb) for p, q in zip(a, b))
    return num / (sum((p-ma)**2 for p in a) * sum((q-mb)**2 for q in b)) ** .5
assert spearman([1,1,2,2],[1,2,1,2]) == 0  # fieldnotes' regression case
msgs = collections.Counter(r['author'] for r in R if not isroot(r))
frozen = sorted(a for a in msgs if msgs[a] >= 60)
print('frozen cohort (>=60 distinct replies): n=%d' % len(frozen)); print(' ', ', '.join(frozen))
for rule in ('R1', 'R2', 'R3'):
    E = collections.Counter()
    for r in R:
        if isroot(r): continue
        for t in targets(r, rule)[0]:
            if t != r['author']: E[(r['author'], t)] += 1
    sent = collections.Counter(); T = collections.defaultdict(set)
    for (a, b), w in E.items(): sent[a] += w; T[a].add(b)
    for label, coh in (('frozen', [a for a in frozen if T[a]]), ('edge-weight>=60', [a for a in sent if sent[a] >= 60])):
        sh = {a: sum((b, a) in E for b in T[a]) / len(T[a]) for a in coh}; nt = {a: len(T[a]) for a in coh}
        xs = sorted(coh, key=lambda a: -nt[a])
        print('%s %-16s n=%2d  rho_tie=%.2f  five widest %.2f  five narrowest %.2f' % (rule, label, len(xs),
              spearman([nt[a] for a in xs], [sh[a] for a in xs]), st.mean(sh[a] for a in xs[:5]), st.mean(sh[a] for a in xs[-5:])))
        if label == 'edge-weight>=60': print('   not in frozen:', sorted(set(coh) - set(frozen)), ' frozen missing:', sorted(set(frozen) - set(coh)))
