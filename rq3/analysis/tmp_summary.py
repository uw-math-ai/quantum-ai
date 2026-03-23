import json
import glob
import os
import statistics
from collections import defaultdict

files = sorted(glob.glob('rq3/data/*/*.json'))


def cfg(meta):
    a = meta.get('max_attempts', 1)
    t = meta.get('timeout', 0)
    if a == 1:
        return '1 attempt'
    if a == 15 and t <= 300:
        return '15 attempts / 300s'
    if a == 15:
        return f'15 attempts / {t}s'
    return f'{a} attempts / {t}s'


rows = []
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    model = os.path.basename(os.path.dirname(f))
    cond = cfg(d.get('metadata', {}))
    for r in d.get('results', []):
        bm = r.get('baseline_metrics') or {}
        om = r.get('optimized_metrics') or {}
        valid = bool(r.get('valid', False))
        better = bool(r.get('better', False))
        success = valid and better
        cx_red = None
        dep_red = None
        if success and bm.get('cx_count', 0) > 0 and 'cx_count' in om:
            cx_red = (bm['cx_count'] - om['cx_count']) / bm['cx_count'] * 100
        if success and bm.get('depth', 0) > 0 and 'depth' in om:
            dep_red = (bm['depth'] - om['depth']) / bm['depth'] * 100
        rows.append({
            'model': model,
            'cond': cond,
            'valid': valid,
            'better': better,
            'success': success,
            'cx': bm.get('cx_count'),
            'depth': bm.get('depth'),
            'elapsed': float(r.get('elapsed_seconds', 0) or 0),
            'cx_red': cx_red,
            'dep_red': dep_red,
        })

print('TOTAL', len(rows))

by_mc = defaultdict(list)
for row in rows:
    by_mc[(row['model'], row['cond'])].append(row)

print('\nBY_MODEL_CONDITION')
for (m, c) in sorted(by_mc):
    rs = by_mc[(m, c)]
    n = len(rs)
    valid = sum(1 for x in rs if x['valid'])
    better = sum(1 for x in rs if x['better'])
    success = sum(1 for x in rs if x['success'])
    med_elapsed = statistics.median([x['elapsed'] for x in rs]) if rs else 0
    cxr = [x['cx_red'] for x in rs if x['cx_red'] is not None]
    dr = [x['dep_red'] for x in rs if x['dep_red'] is not None]
    mean_cxr = sum(cxr) / len(cxr) if cxr else 0
    mean_dr = sum(dr) / len(dr) if dr else 0
    print(
        f'{m}|{c}|n={n}|valid={valid/n*100:.1f}|better={better/n*100:.1f}'
        f'|success={success/n*100:.1f}|elapsed_med={med_elapsed:.1f}'
        f'|cx_red={mean_cxr:.1f}|dep_red={mean_dr:.1f}'
    )

by_cond = defaultdict(list)
for row in rows:
    by_cond[row['cond']].append(row)

order = ['1 attempt', '15 attempts / 300s', '15 attempts / 900s']
print('\nPOOLED_BY_CONDITION')
for c in sorted(by_cond, key=lambda x: order.index(x) if x in order else 99):
    rs = by_cond[c]
    n = len(rs)
    valid = sum(1 for x in rs if x['valid'])
    better = sum(1 for x in rs if x['better'])
    success = sum(1 for x in rs if x['success'])
    print(f'{c}|n={n}|valid={valid/n*100:.1f}|better={better/n*100:.1f}|success={success/n*100:.1f}')

cx_vals = sorted([x['cx'] for x in rows if isinstance(x['cx'], (int, float))])
q1 = cx_vals[len(cx_vals) // 4]
q2 = cx_vals[len(cx_vals) // 2]
q3 = cx_vals[(3 * len(cx_vals)) // 4]
print(f'\nCX_CUTOFFS|q1={q1}|q2={q2}|q3={q3}')


def cx_bin(v):
    if v is None:
        return 'unknown'
    if v <= q1:
        return 'small'
    if v <= q2:
        return 'medium'
    if v <= q3:
        return 'large'
    return 'xlarge'


by_bin = defaultdict(list)
for row in rows:
    by_bin[cx_bin(row['cx'])].append(row)

print('SUCCESS_BY_CX_BIN')
for b in ['small', 'medium', 'large', 'xlarge', 'unknown']:
    if b not in by_bin:
        continue
    rs = by_bin[b]
    n = len(rs)
    valid = sum(1 for x in rs if x['valid'])
    better = sum(1 for x in rs if x['better'])
    success = sum(1 for x in rs if x['success'])
    print(f'{b}|n={n}|valid={valid/n*100:.1f}|better={better/n*100:.1f}|success={success/n*100:.1f}')

print('\nBEST_CONDITION_PER_MODEL')
per_model = defaultdict(dict)
for (m, c), rs in by_mc.items():
    n = len(rs)
    success = sum(1 for x in rs if x['success']) / n * 100
    per_model[m][c] = success
for m in sorted(per_model):
    best_c = max(per_model[m], key=per_model[m].get)
    print(f'{m}|best={best_c}|success={per_model[m][best_c]:.1f}')
