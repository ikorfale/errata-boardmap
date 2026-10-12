"""Exploratory (amendment 5, 12 Oct, asked by clearreason_assistant on Moltbook): caller-level view.
Calls from one caller are not independent. Each caller gets the mean actors of their calls in a group;
groups are compared by the median of caller means, and a cluster bootstrap (resampling callers) gives an
interval for the ratio of mean actors in-thread / outside. Usage: caller_level.py door_mine.tsv"""
import json, sys, random, statistics as st
exec(open('door_count.py').read().split('D = [door(f)')[0])  # same labels and revisions as door_count.py
d = door(sys.argv[1])
rows = [r for r in F.values() if r.get('cta') == 'yes' and r.get('locus') != 'poll' and not r.get('outside_unknown')]
def grp(r, how):
    if how == 'primary': return 'in-thread' if r['locus'] == 'thread' else 'outside'
    return 'board' if r['locus'] == 'thread' else d.get(r['seq'], '?')
for how in ('primary', 'door'):
    by = {}
    for r in rows: by.setdefault(grp(r, how), {}).setdefault(r['caller'], []).append(len(r['actors']))
    print(f'\n{how}:')
    for k, cs in sorted(by.items()):
        means = [st.mean(v) for v in cs.values()]
        print(f'  {k:9s} calls={sum(map(len, cs.values())):3d} callers={len(cs):3d}  median of caller means {st.median(means):.2f}  '
              f'callers with 0 actors on every call {sum(m == 0 for m in means)}')
by = {}
for r in rows: by.setdefault(r['caller'], []).append((grp(r, 'primary'), len(r['actors'])))
callers = sorted(by); random.seed(12); R = []
for _ in range(10000):
    s = [x for c in random.choices(callers, k=len(callers)) for x in by[c]]
    i = [a for g, a in s if g == 'in-thread']; o = [a for g, a in s if g == 'outside']
    if i and o and st.mean(o) > 0: R.append(st.mean(i) / st.mean(o))
R.sort(); obs_i = [a for v in by.values() for g, a in v if g == 'in-thread']; obs_o = [a for v in by.values() for g, a in v if g == 'outside']
print(f'\nratio of mean actors in-thread/outside: {st.mean(obs_i) / st.mean(obs_o):.2f}  '
      f'caller-bootstrap 95% [{R[int(.025 * len(R))]:.2f}, {R[int(.975 * len(R))]:.2f}]  (n={len(R)} resamples; prereg threshold 3x)')
