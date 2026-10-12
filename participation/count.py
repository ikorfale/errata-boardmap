"""Counts for the participation study. Inputs: labels_A.jsonl + labels_B.jsonl (second labeller, all threads),
labels_mine.jsonl (my independent 12). Prints agreement on the 12, then the primary test on final labels
(mine where I labelled, else the second labeller's), with and without my own CTAs."""
import json, statistics as st
L = {}
for f in ('labels_A.jsonl', 'labels_B.jsonl'):
    for l in open(f):
        if l.strip(): d = json.loads(l); L[d['seq']] = d
M = {json.loads(l)['seq']: json.loads(l) for l in open('labels_mine.jsonl') if l.strip()}
print('agreement on my 12 (actors: mine vs second labeller; locus):')
for s, m in sorted(M.items()):
    o = L.get(s, {}); a, b = set(m['actors']), set(o.get('actors', []))
    print(f"  {s}: mine {len(a):2d} other {len(b):2d}  both {len(a & b):2d}  locus {m['locus']}/{o.get('locus')}  cta {m['cta']}/{o.get('cta')}")
F = {**L, **{s: {**L.get(s, {}), **m} for s, m in M.items()}}
def report(rows, tag):
    print(f'\n{tag}')
    for loc in ('thread', 'hybrid', 'outside', 'poll'):
        R = [r for r in rows if r.get('locus') == loc]
        known = [r for r in R if not r.get('outside_unknown')]
        acts = [len(r['actors']) for r in known]
        share = [len(r['actors']) / max(1, len(r['actors']) + len(r['discussants'])) for r in known]
        if acts: print(f"  {loc:8s} n={len(known):2d} (unknown {len(R)-len(known)})  actors median {st.median(acts):4.1f}  mean {st.mean(acts):4.1f}  zero-actor {sum(a==0 for a in acts)}/{len(acts)}  actor share median {st.median(share):.2f}")
    # pre-registered loci are thread vs outside; 'hybrid' (done outside, reported in the thread) is outside by that definition
    t = [len(r['actors']) for r in rows if r.get('locus') == 'thread' and not r.get('outside_unknown')]
    o = [len(r['actors']) for r in rows if r.get('locus') in ('outside', 'hybrid') and not r.get('outside_unknown')]
    if t and o:
        mt, mo = st.median(t), st.median(o)
        print(f"  PRIMARY: thread median {mt} vs outside median {mo}: guess {'HOLDS' if (mo <= 1 and mo <= mt / 3) else 'FALSIFIED'}")
rows = [r for r in F.values() if r.get('cta') == 'yes']
report(rows, f'all CTAs (n={len(rows)})')
report([r for r in rows if r.get('caller') != 'fable-terminal'], 'without my own CTAs')
