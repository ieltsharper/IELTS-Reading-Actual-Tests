"""Checks data/<volume>.json: every test has questions 1-40 exactly once, every question has a key, gaps match,
choices are valid. Usage: python -X utf8 -I _generator/check_data.py data/vol-1.json [test number]"""
import json, sys, re, collections

d = json.load(open(sys.argv[1], encoding='utf-8'))
only = int(sys.argv[2]) if len(sys.argv) > 2 else None
bad = []
by_test = collections.defaultdict(list)
for p in d['passages']:
    t = int(p['group'].split()[1])
    if only and t != only:
        continue
    where = p['label']
    nums = []
    if not p['body'] or sum(len(''.join(r.get('t', '') for r in b['runs'])) for b in p['body']) < 800:
        bad.append('%s: passage text looks too short' % where)
    for g in p['groups']:
        nums += g['numbers']
        if g['type'] == 'multi':
            k = g['key']
            if len(k['accept']) != g['choose']:
                bad.append('%s %s: multi choose mismatch' % (where, g['title']))
            letters = [o['key'] for o in g['options']]
            for a in k['accept']:
                if a not in letters:
                    bad.append('%s %s: answer %s not an option' % (where, g['title'], a))
            continue
        gaps = []
        if g['type'] in ('gap', 'bank'):
            def walk(blocks):
                for b in blocks:
                    if b['type'] == 'table':
                        for row in b['rows']:
                            for cell in row:
                                walk(cell)
                    else:
                        for r in b.get('runs', []):
                            if 'gap' in r and r.get('part') != 2:
                                gaps.append(r['gap'])
            walk(g['content'])
            if sorted(gaps) != sorted(g['numbers']):
                bad.append('%s %s: gaps in the text %s != numbers %s' % (where, g['title'], sorted(gaps), g['numbers']))
        for n in g['numbers']:
            k = p['key'].get(str(n))
            if not k or not k['answer'] or not str(k['answer']).strip():
                bad.append('%s Q%d: no answer' % (where, n))
                continue
            if g['type'] in ('tfng', 'ynng'):
                if k['answer'] not in g['choices']:
                    bad.append('%s Q%d: answer %r not in %s' % (where, n, k['answer'], g['choices']))
            if g['type'] in ('match', 'grid', 'headings', 'bank'):
                letters = [o['key'] for o in g['options']['list']] if g.get('options') else g['letters']
                if k['answer'] not in letters:
                    bad.append('%s Q%d: answer %r not among %s' % (where, n, k['answer'], letters))
            if g['type'] == 'mcq':
                q = [x for x in g['questions'] if x['n'] == n][0]
                if k['answer'] not in [o['key'] for o in q['options']]:
                    bad.append('%s Q%d: answer %r not an option' % (where, n, k['answer']))
        if g['type'] in ('tfng', 'ynng', 'short', 'mcq', 'match', 'grid', 'headings'):
            have = [q['n'] for q in g['questions']]
            if have != g['numbers']:
                bad.append('%s %s: items %s != range' % (where, g['title'], have))
    by_test[t] += nums
for t, nums in sorted(by_test.items()):
    if sorted(nums) != list(range(1, 41)):
        bad.append('Test %d: questions %s are not exactly 1-40' % (t, sorted(nums)))
for line in bad:
    print('PROBLEM:', line)
print('OK' if not bad else '%d problems' % len(bad))
sys.exit(1 if bad else 0)
