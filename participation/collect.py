"""Candidate CTAs: walk /v1/search for each pre-registered query (after=1 forward to next_after null), keep posts in the window.
Writes raw/<query>.jsonl and candidates.jsonl (deduped by id, with the queries that hit)."""
import json, subprocess, os, time, urllib.parse
Q = ['join', 'play', 'register', 'players', 'submit', 'sign up', 'participate', 'round', 'your guess', 'commit', 'label', 'challenge', 'entries']
T0, T1 = 1790121600, 1791763200  # 2026-09-23 00:00Z .. 2026-10-12 00:00Z
os.makedirs('raw', exist_ok=True); cand = {}
def get(p): return json.loads(subprocess.run([os.environ.get('BOARD_GET', './get.sh'), p], capture_output=True, text=True).stdout)
for q in Q:
    a, n, out = 1, 0, open(f"raw/{q.replace(' ', '_')}.jsonl", 'w')
    while True:
        d = get(f"/v1/search?q={urllib.parse.quote(q)}&after={a}&limit=30")
        for it in d.get('items', []):
            out.write(json.dumps(it) + '\n'); n += 1
            if T0 <= it.get('created_at', 0) < T1:
                c = cand.setdefault(it['id'], {k: it.get(k) for k in ('id', 'seq', 'author', 'kind', 'root_id', 'root_seq', 'thread_id', 'created_at', 'title', 'preview', 'thread_reply_count')})
                c.setdefault('queries', []).append(q)
        if not d.get('next_after') or not d.get('items'): break
        a = d['next_after']; time.sleep(0.3)
    print(q, n, flush=True)
with open('candidates.jsonl', 'w') as f:
    for c in sorted(cand.values(), key=lambda c: c['seq']): f.write(json.dumps(c, ensure_ascii=False) + '\n')
print('candidates in window', len(cand))
