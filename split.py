#!/usr/bin/env python3
"""Ignored or broadcasting? Same edge rule as boardmap.py. For each sender with 60+ replies, split their
targets by the size of the thread where the sender replied to them (replies in that root inside the 96h window):
small < 10, big >= 30. Share = targets who answered the sender back anywhere in the window."""
import json, re, collections
D = 'lab/boardmap/'
R = [json.loads(l) for l in open('data/activity_96h_0930.jsonl')]
isroot = lambda r: not r.get('root_id') or r['root_id'] == r['id']
root_author = {r['id']: r['author'] for r in R if isroot(r)}
for k, v in json.load(open(D + 'root_authors.json')).items():
    if v.get('author'): root_author[k] = v['author']
names = {r['author'] for r in R} | set(root_author.values())
size = collections.Counter(r['root_id'] for r in R if not isroot(r))
E = collections.Counter(); where = collections.defaultdict(list)
for r in R:
    if isroot(r): continue
    m = re.match(r'\s*@([\w-]+)', r.get('preview') or '')
    t = m.group(1) if m and m.group(1) in names else root_author.get(r['root_id'])
    if t and t != r['author']:
        E[(r['author'], t)] += 1; where[(r['author'], t)].append(size[r['root_id']])
sent = collections.Counter()
for (a, b), w in E.items(): sent[a] += w
print('threads in window %d; replies-per-thread median %d' % (len(size), sorted(size.values())[len(size)//2]))
print('%-28s %9s %9s %9s' % ('sender', 'all', 'small<10', 'big>=30'))
rows = []
for a in sent:
    if sent[a] < 60: continue
    T = [b for (x, b) in E if x == a]
    def share(sel):
        s = [b for b in T if sel(where[(a, b)])]
        return (sum((b, a) in E for b in s), len(s))
    al = share(lambda w: True); sm = share(lambda w: min(w) < 10); bg = share(lambda w: min(w) >= 30)
    rows.append((al[0] / al[1], a, al, sm, bg))
f = lambda p: '%d/%d=%.2f' % (p[0], p[1], p[0] / p[1]) if p[1] else '-'
for s, a, al, sm, bg in sorted(rows): print('%-28s %9s %12s %12s' % (a, f(al), f(sm), f(bg)))
# pooled: bottom five vs top five by overall share
for lab, grp in (('bottom5', sorted(rows)[:5]), ('top5', sorted(rows)[-5:])):
    for k, i in (('small', 3), ('big', 4)):
        n = sum(g[i][0] for g in grp); d = sum(g[i][1] for g in grp)
        print(lab, k, '%d/%d=%.2f' % (n, d, n / d if d else 0))
# confound: was the target still active? count unanswered targets who posted anything after the sender's first reply to them
last = collections.defaultdict(int); first = {}
for r in R: last[r['author']] = max(last[r['author']], r['created_at'])
for r in R:
    if isroot(r): continue
    m = re.match(r'\s*@([\w-]+)', r.get('preview') or '')
    t = m.group(1) if m and m.group(1) in names else root_author.get(r['root_id'])
    if t and t != r['author']: first.setdefault((r['author'], t), r['created_at'])
for lab, grp in (('bottom5', sorted(rows)[:5]), ('top5', sorted(rows)[-5:])):
    un = [(g[1], b) for g in grp for (x, b) in E if x == g[1] and (b, g[1]) not in E]
    act = sum(last[b] > first[(a, b)] for a, b in un)
    print(lab, 'unanswered targets %d, of them posted later in window %d (%.2f)' % (len(un), act, act / len(un) if un else 0))
