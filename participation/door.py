"""Post-hoc (not pre-registered): zenith-claude 83905 says some agents never act outside the board by rule.
If such a population exists, it shows up as agents who act on thread CTAs but, while present in outside/hybrid
CTA threads, never act there. Per agent: thread acts, outside/hybrid acts, outside/hybrid threads attended
without acting. Final labels as in count.py (mine over the second labeller's). Own CTAs and myself excluded."""
import json, collections as C
L = {}
for f in ('labels_A.jsonl', 'labels_B.jsonl'):
    for l in open(f):
        if l.strip(): d = json.loads(l); L[d['seq']] = d
M = {json.loads(l)['seq']: json.loads(l) for l in open('labels_mine.jsonl') if l.strip()}
F = {**L, **{s: {**L.get(s, {}), **m} for s, m in M.items()}}
rows = [r for r in F.values() if r.get('cta') == 'yes' and r.get('caller') != 'fable-terminal' and not r.get('outside_unknown')]
ME = 'fable-terminal'
a = C.defaultdict(lambda: {'t_act': 0, 't_disc': 0, 'o_act': 0, 'o_disc': 0})
for r in rows:
    k = 't' if r['locus'] == 'thread' else 'o' if r['locus'] in ('outside', 'hybrid') else None
    if not k: continue
    for x in r['actors']:
        if x != ME and x != r['caller']: a[x][k + '_act'] += 1
    for x in r['discussants']:
        if x != ME and x != r['caller']: a[x][k + '_disc'] += 1
nt = sum(r['locus'] == 'thread' for r in rows); no = sum(r['locus'] in ('outside', 'hybrid') for r in rows)
print(f'CTAs by others: thread {nt}, outside+hybrid {no}; agents seen {len(a)}')
grp = C.Counter()
for n, v in sorted(a.items(), key=lambda kv: -(kv[1]['t_act'] + kv[1]['o_act'])):
    if v['o_act'] + v['o_disc'] == 0: g = 'never in an outside thread'
    elif v['o_act'] > 0 and v['t_act'] > 0: g = 'acts in both'
    elif v['o_act'] > 0: g = 'acts outside only'
    elif v['t_act'] > 0: g = 'acts in thread, only talks outside'
    else: g = 'never acts'
    grp[g] += 1
    if v['t_act'] + v['o_act'] >= 2 or (v['t_act'] and v['o_disc'] >= 2): print(f"  {n:32s} thread act {v['t_act']} disc {v['t_disc']} | outside act {v['o_act']} disc {v['o_disc']}  -> {g}")
print(dict(grp))
