"""Amendment 4: how actors on read-door calls acted (HOW_CODING.md). Coder file + my overrides from the spot check."""
import json, statistics as st
R = [json.loads(l) for l in open('read_door_how.jsonl') if l.strip()]
for o in (json.loads(l) for l in open('read_door_overrides.jsonl') if l.strip()):
    for r in R:
        if r['seq'] == o['seq'] and r.get('actor') == o.get('actor') and ('actor' in o or 'requires_running_callers_code' in r):
            r.update({k: v for k, v in o.items() if k != 'why'})
P = [r for r in R if 'actor' in r]; C = {r['seq']: r['requires_running_callers_code'] for r in R if 'actor' not in r}
from collections import Counter
print('pairs', len(P), dict(Counter(r['code'] for r in P)))
calls = sorted(C)
for label, keep in (('ran', {'ran'}), ('ran or read', {'ran', 'read'}), ('any action', {'ran', 'read', 'substitute', 'unclear'})):
    v = [sum(r['seq'] == s and r['code'] in keep for r in P) for s in calls]
    print(f'{label:12s} per call {v}  median {st.median(v)}  zero {sum(x == 0 for x in v)}/10')
print('requires running the caller\'s code:', sum(v == 'yes' for v in C.values()), 'of', len(C))
