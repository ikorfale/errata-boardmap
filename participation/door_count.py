"""Exploratory (amendment 3): actors per CTA by door. thread-locus CTAs are door=board by definition; non-thread CTAs
take their door from a coder file. Usage: door_count.py door_mine.tsv [door_blind.tsv]. Prints agreement if two."""
import json, sys, statistics as st
L = {}
for f in ('labels_A.jsonl', 'labels_B.jsonl'):
    for l in open(f):
        if l.strip(): d = json.loads(l); L[d['seq']] = d
M = {json.loads(l)['seq']: json.loads(l) for l in open('labels_mine.jsonl') if l.strip()}
F = {**L, **{s: {**L.get(s, {}), **m} for s, m in M.items()}}
for l in open('revisions.jsonl'):  # full-thread author sweep, 12 Oct: authors the labeller never classified
    v = json.loads(l); r = F[v['seq']]
    r['actors'] = list(dict.fromkeys(r['actors'] + v['add_actors'])); r['discussants'] = list(dict.fromkeys(r['discussants'] + v['add_discussants']))
def door(f): return {int(l.split('\t')[0]): l.split('\t')[1].strip() for l in open(f) if l[0].isdigit()}
D = [door(f) for f in sys.argv[1:]]
if len(D) == 2:
    both = sorted(set(D[0]) & set(D[1])); agree = [s for s in both if D[0][s] == D[1][s]]
    print(f'agreement {len(agree)}/{len(both)}; differ:', [(s, D[0][s], D[1][s]) for s in both if s not in agree])
for i, d in enumerate(D):
    rows = [r for r in F.values() if r.get('cta') == 'yes' and r.get('locus') != 'poll' and not r.get('outside_unknown')]
    print(f'\ncoder {sys.argv[1 + i]}')
    for own in (True, False):
        g = {}
        for r in rows:
            if not own and r['caller'] == 'fable-terminal': continue
            k = 'board' if r['locus'] == 'thread' else d.get(r['seq'], '?')
            g.setdefault(k, []).append(len(r['actors']))
        print('  ' + ('all' if own else 'without my CTAs') + ': ' + '  '.join(
            f"{k} n={len(v)} median {st.median(v)} zero {sum(a == 0 for a in v)}" for k, v in sorted(g.items())))
