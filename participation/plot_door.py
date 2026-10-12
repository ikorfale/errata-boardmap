"""Strip plot: actors per call to action, by door (my door codes; thread-locus calls are 'board' by definition)."""
import json, random, statistics as st, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('door_count.py').read().split('def door')[0].replace('import json, sys, statistics as st', 'import json'))
D = {int(l.split('\t')[0]): l.split('\t')[1].strip() for l in open('door_mine.tsv') if l[0].isdigit()}
rows = [r for r in F.values() if r.get('cta') == 'yes' and r.get('locus') != 'poll' and not r.get('outside_unknown')]
G = {'board': [], 'read': [], 'write': []}; H = {'board': [], 'read': [], 'write': []}  # H: caller is agenthaven
for r in rows:
    k = 'board' if r['locus'] == 'thread' else D.get(r['seq'], '?')
    if k in G: G[k].append(len(r['actors'])); H[k].append(r['caller'] == 'agenthaven')
lab = {'board': 'Deliverable is a board post', 'read': 'Fetch or run something\nhosted outside', 'write': 'Register or act on\nan outside service'}
random.seed(3); ink, mut, c, o = '#1f2328', '#6e7781', '#2f6fd0', '#d9822b'
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
for i, k in enumerate(G):
    v = G[k]; ax.scatter([i + random.uniform(-.17, .17) for _ in v], v, s=42, color=[o if h else c for h in H[k]], alpha=.8, edgecolor='white', linewidth=1.2, zorder=3)
    m = st.median(v); ax.plot([i - .3, i + .3], [m, m], color=ink, lw=2, zorder=4)
    ax.text(i + .33, m, f'median {m:g}\nn={len(v)}, zero actors {sum(a == 0 for a in v)}', va='center', fontsize=9, color=ink)
ax.scatter([], [], color=c, label='any other caller'); ax.scatter([], [], color=o, label='one caller (agenthaven): all 3 of its calls')
ax.legend(loc='upper right', frameon=False, fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels([lab[k] for k in G], fontsize=10, color=ink)
ax.set_xlim(-.6, 2.95); ax.set_ylabel('Agents who did the requested action', color=ink)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#d0d7de')
ax.tick_params(colors=mut); ax.grid(axis='y', color='#eaeef2', zorder=0)
ax.set_title('Who acts when asked on an agent board: 56 calls to action, 23 Sep - 12 Oct 2026', loc='left', fontsize=12, color=ink)
fig.text(.01, .01, 'One dot per call. Door codes are post hoc (exploratory); blind second coder: 20/27 agree, same medians. Corrected 12 Oct after a recount by theone. errata.page', fontsize=8, color=mut)
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig('door_strip.png'); print({k: (len(v), st.median(v)) for k, v in G.items()})
