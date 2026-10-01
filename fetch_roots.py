#!/usr/bin/env python3
"""Fetch author of every root referenced by the 96h activity file but older than the window. Polite: 0.4 s apart."""
import json, subprocess, time, os
R = [json.loads(l) for l in open('data/activity_96h_0930.jsonl')]
roots = {r['id']: r['author'] for r in R if not r.get('root_id') or r.get('root_id') == r['id']}
need = sorted({r['root_id'] for r in R if r.get('root_id') and r['root_id'] not in roots})
out = 'lab/boardmap/root_authors.json'; have = json.load(open(out)) if os.path.exists(out) else {}
for i, rid in enumerate(need):
    if rid in have: continue
    try:
        d = json.loads(subprocess.run(['./get.sh', '/v1/posts/%s?limit=1' % rid], capture_output=True, text=True, timeout=30).stdout)
        p = d.get('post', {}); have[rid] = {'author': p.get('author'), 'topic': p.get('topic'), 'title': p.get('title'), 'seq': p.get('seq')}
    except Exception as e:
        have[rid] = {'error': str(e)[:100]}
    if i % 20 == 0: json.dump(have, open(out, 'w'))
    time.sleep(0.4)
json.dump(have, open(out, 'w')); print('done', len(have), sum(1 for v in have.values() if v.get('author')))
