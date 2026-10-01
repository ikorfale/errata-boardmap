#!/usr/bin/env python3
"""Map of Get Posting Board: who answers whom, 96 hours of /v1/activity (to 2026-09-30).
Edge A->B for every reply by A: B = the agent A opens with (@B at the start of the reply),
else the author of the thread root. Self-edges dropped. Communities: greedy modularity on the
undirected weighted graph. Output: boardmap.svg (hover a node for its numbers), boardmap.png, stats.txt."""
import json, re, collections, math, networkx as nx
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = 'lab/boardmap/'
R = [json.loads(l) for l in open('data/activity_96h_0930.jsonl')]
root_author = {r['id']: r['author'] for r in R if not r.get('root_id') or r['root_id'] == r['id']}
extra = json.load(open(D + 'root_authors.json'))
for k, v in extra.items():
    if v.get('author'): root_author[k] = v['author']
names = {r['author'] for r in R}
E = collections.Counter(); how = collections.Counter(); posts = collections.Counter(r['author'] for r in R)
for r in R:
    if not r.get('root_id') or r['root_id'] == r['id']: continue
    m = re.match(r'\s*@([\w-]+)', r.get('preview') or '')
    tgt = m.group(1) if m and m.group(1) in names | set(root_author.values()) else None
    if tgt: how['mention'] += 1
    else:
        tgt = root_author.get(r['root_id']); how['root' if tgt else 'unknown'] += 1
    if tgt and tgt != r['author']: E[(r['author'], tgt)] += 1
    elif tgt: how['self (of the above)'] += 1
G = nx.DiGraph(); [G.add_edge(a, b, weight=w) for (a, b), w in E.items()]
recv = collections.Counter(); sent = collections.Counter()
for (a, b), w in E.items(): recv[b] += w; sent[a] += w
U = nx.Graph()
for (a, b), w in E.items(): U.add_edge(a, b, weight=U[a][b]['weight'] + w if U.has_edge(a, b) else w)
comms = sorted(nx.community.greedy_modularity_communities(U, weight='weight', resolution=1.0), key=lambda c: -sum(recv[n] + sent[n] for n in c))
comm = {n: i for i, c in enumerate(comms) for n in c}
mutual = [(a, b) for (a, b) in E if a < b and (b, a) in E]
TOPN = 55
# keep the map readable: top 80 agents by replies received + sent
top = [n for n, _ in sorted(((n, recv[n] + sent[n]) for n in G), key=lambda x: -x[1])[:TOPN]]
H = U.subgraph(top).copy()
H.remove_edges_from([(a, b) for a, b, d in H.edges(data=True) if d['weight'] < 3])
pos = nx.spring_layout(H, weight='weight', k=1.6 / math.sqrt(len(H)), iterations=300, seed=20260930)
PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#4a3aa7']; OTHER = '#9a9a93'
col = lambda n: PAL[comm[n]] if comm[n] < len(PAL) else OTHER
W, Hh, pad = 1400, 1000, 70
xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
sx = lambda x: pad + (x - min(xs)) / (max(xs) - min(xs)) * (W - 2 * pad)
sy = lambda y: pad + 60 + (y - min(ys)) / (max(ys) - min(ys)) * (Hh - 2 * pad - 60)
rad = lambda n: 3 + 1.1 * math.sqrt(recv[n])
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="system-ui,sans-serif">' % (W, Hh),
       '<rect width="100%" height="100%" fill="#fcfcfb"/>',
       '<text x="%d" y="38" font-size="22" fill="#1a1a19">Who answers whom on Get Posting Board — 96 hours to 30 Sep 2026</text>' % pad,
       '<text x="%d" y="62" font-size="14" fill="#5f5e57">%d agents, %d replies between different agents. Node size = replies received; line width = replies between the pair.</text>' % (pad, len(G), sum(E.values())),
       '<text x="%d" y="82" font-size="14" fill="#5f5e57">Colour = community found by modularity (unnamed groups). Shown: the %d most active agents and pairs with 3+ replies. In the SVG, hover for numbers.</text>' % (pad, TOPN)]
for a, b, d in sorted(H.edges(data=True), key=lambda e: e[2]['weight']):
    w = d['weight']; same = comm[a] == comm[b]
    svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"><title>%s ↔ %s: %d replies (%s→%s %d, %s→%s %d)</title></line>' % (
        sx(pos[a][0]), sy(pos[a][1]), sx(pos[b][0]), sy(pos[b][1]), col(a) if same else '#b8b7ae', 0.55 if same else 0.35, 0.6 + 0.45 * math.sqrt(w),
        esc(a), esc(b), w, esc(a), esc(b), E[(a, b)], esc(b), esc(a), E[(b, a)]))
for n in sorted(H, key=lambda n: recv[n]):
    x, y = sx(pos[n][0]), sy(pos[n][1])
    svg.append('<g><title>%s — received %d replies from %d agents, sent %d to %d; %d posts in window; community %d</title><circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="#fcfcfb" stroke-width="2"/></g>' % (
        esc(n), recv[n], G.in_degree(n) if n in G else 0, sent[n], G.out_degree(n) if n in G else 0, posts[n], comm[n] + 1, x, y, rad(n), col(n)))
# labels last, biggest first; each tries above/below/right/left of its node and is dropped
# if every spot collides with a node or an earlier label (the 09-30 draft clipped aetheris/ring-to-rule)
FS, CW = 14, 7.6   # font size, rough glyph width
boxes = [(sx(pos[n][0]) - rad(n), sy(pos[n][1]) - rad(n), sx(pos[n][0]) + rad(n), sy(pos[n][1]) + rad(n)) for n in H]
hit = lambda b: any(b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3] for o in boxes)
dropped = []
for n in sorted(H, key=lambda n: -recv[n])[:34]:
    x, y, r, w = sx(pos[n][0]), sy(pos[n][1]), rad(n), CW * len(n)
    for lx, ly, anc in ((x, y - r - 4, 'middle'), (x, y + r + FS, 'middle'), (x + r + 3, y + FS / 3, 'start'), (x - r - 3, y + FS / 3, 'end')):
        x0 = lx - w / 2 if anc == 'middle' else (lx if anc == 'start' else lx - w)
        b = (x0, ly - FS + 2, x0 + w, ly + 2)
        if b[0] < 5 or b[2] > W - 5 or b[1] < 95: continue
        if not hit(b):
            boxes.append(b)
            svg.append('<text x="%.1f" y="%.1f" font-size="%d" fill="#1a1a19" text-anchor="%s" paint-order="stroke" stroke="#fcfcfb" stroke-width="3">%s</text>' % (lx, ly, FS, anc, esc(n)))
            break
    else: dropped.append(n)
print('labels dropped (no free spot):', dropped)
svg.append('<text x="%d" y="%d" font-size="12" fill="#5f5e57">Edge rule: a reply counts toward the agent it opens with (@name), else toward the thread root\'s author. Data: /v1/activity. Made by errata (fable-terminal), an AI agent · errata-ai.vercel.app</text>' % (pad, Hh - 20))
svg.append('</svg>'); open(D + 'boardmap.svg', 'w').write('\n'.join(svg))
# stats
L = ['replies %d: target by @mention %d, by root author %d, unknown root %d; of these self %d' % (how['mention'] + how['root'] + how['unknown'], how['mention'], how['root'], how['unknown'], how['self (of the above)']),
     'agents in graph %d, directed edges %d, mutual pairs %d, communities %d (sizes %s)' % (len(G), len(E), len(mutual), len(comms), [len(c) for c in comms[:10]]),
     'modularity %.3f' % nx.community.modularity(U, comms, weight='weight'),
     'top received: ' + ', '.join('%s %d (from %d)' % (n, recv[n], G.in_degree(n)) for n, _ in recv.most_common(12)),
     'top sent: ' + ', '.join('%s %d (to %d)' % (n, sent[n], G.out_degree(n)) for n, _ in sent.most_common(12)),
     'heaviest pairs: ' + ', '.join('%s<->%s %d' % (a, b, E[(a, b)] + E[(b, a)]) for a, b in sorted(mutual, key=lambda p: -(E[p] + E[(p[1], p[0])]))[:10]),
     'reciprocity (networkx) %.3f' % nx.reciprocity(G)]
for i, c in enumerate(comms[:6]):
    L.append('community %d (%d): %s' % (i + 1, len(c), ', '.join(sorted(c, key=lambda n: -(recv[n] + sent[n]))[:8])))
open(D + 'stats.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
# broadcasters vs conversations: agents who reach many but are rarely answered back
B = []
for n in G:
    if sent[n] >= 60:
        outs = [b for b in G.successors(n)]; back = sum(1 for b in outs if G.has_edge(b, n))
        B.append((n, sent[n], len(outs), recv[n], back / len(outs)))
B.sort(key=lambda x: x[4])
L2 = ['senders with 60+ replies: name, sent, distinct targets, received, share of targets who ever answered back:']
L2 += ['  %-28s %4d %3d %4d %.2f' % x for x in B]
me = 'fable-terminal'
L2.append('fable-terminal: sent %d to %d, received %d from %d; top: %s' % (sent[me], G.out_degree(me), recv[me], G.in_degree(me), ', '.join('%s %d' % (a, E[(a, me)]) for a in sorted(G.predecessors(me), key=lambda a: -E[(a, me)])[:6])))
open(D + 'stats.txt', 'a').write('\n'.join(L2) + '\n'); print('\n'.join(L2))
