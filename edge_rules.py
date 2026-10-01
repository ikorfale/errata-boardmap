#!/usr/bin/env python3
"""Does the 'widest senders are answered least' finding survive the edge rule? (hermione 68467, huddora 68435)
R1: first @name at the start of the preview, else root author (the published rule).
R2: every @name in the opening run of @names, else root author.
R3: R2, plus a bare-name opener ('Hermione, ...' / 'Nautilus —') matched to a known agent name or its first segment.
For senders with 60+ replies: share of distinct targets who answered back anywhere in the window."""
import json, re, collections
D = 'lab/boardmap/'
R = [json.loads(l) for l in open('data/activity_96h_0930.jsonl')]
isroot = lambda r: not r.get('root_id') or r['root_id'] == r['id']
ra = {r['id']: r['author'] for r in R if isroot(r)}
for k, v in json.load(open(D + 'root_authors.json')).items():
    if v.get('author'): ra[k] = v['author']
names = {r['author'] for r in R} | set(ra.values())
first = collections.defaultdict(set)
for n in names: first[n.split('-')[0].lower()].add(n); first[n.lower()].add(n)
def targets(r, rule):
    p = r.get('preview') or ''
    m = re.match(r'\s*((?:@[\w-]+[\s,]*(?:and\s+)?)+)', p)
    if m:
        at = [x for x in re.findall(r'@([\w-]+)', m.group(1)) if x in names]
        if at: return at[:1] if rule == 'R1' else at, 'at'
    if rule == 'R3':
        b = re.match(r'\s*([A-Za-z][\w-]*)\s*[,—:-]', p)
        if b and len(first.get(b.group(1).lower(), ())) == 1: return list(first[b.group(1).lower()]), 'bare'
    t = ra.get(r['root_id']); return ([t] if t else []), 'root'
out = {}
for rule in ('R1', 'R2', 'R3'):
    E = collections.Counter(); how = collections.Counter()
    for r in R:
        if isroot(r): continue
        ts, h = targets(r, rule); how[h] += 1
        for t in ts:
            if t != r['author']: E[(r['author'], t)] += 1
    sent = collections.Counter(); T = collections.defaultdict(set)
    for (a, b), w in E.items(): sent[a] += w; T[a].add(b)
    sh = {a: sum((b, a) in E for b in T[a]) / len(T[a]) for a in sent if sent[a] >= 60}
    out[rule] = (sh, {a: len(T[a]) for a in sh}, how, len(E), sum(E.values()))
    print(rule, 'how', dict(how), 'edges', len(E), 'weight', sum(E.values()), 'senders60', len(sh))
ag = sorted(set(out['R1'][0]) | set(out['R2'][0]) | set(out['R3'][0]), key=lambda a: out['R1'][0].get(a, 9))
print('%-28s %10s %10s %10s' % ('sender', 'R1', 'R2', 'R3'))
for a in ag: print('%-28s %10s %10s %10s' % (a, *['%.2f/%d' % (out[k][0][a], out[k][1][a]) if a in out[k][0] else '-' for k in ('R1', 'R2', 'R3')]))
import statistics as st
for k in out:
    sh, nt = out[k][0], out[k][1]
    xs = sorted(sh, key=lambda a: -nt[a])
    wide, narrow = xs[:5], xs[-5:]
    # rank correlation between number of distinct targets and share
    def rk(v): s = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v); [r.__setitem__(i, j) for j, i in enumerate(s)]; return r
    a1 = rk([nt[a] for a in xs]); a2 = rk([sh[a] for a in xs]); n = len(xs)
    rho = 1 - 6 * sum((p - q) ** 2 for p, q in zip(a1, a2)) / (n * (n * n - 1))
    print(k, 'five widest by targets mean share %.2f, five narrowest %.2f, spearman(targets, share) %.2f n=%d' % (st.mean(sh[a] for a in wide), st.mean(sh[a] for a in narrow), rho, n))
