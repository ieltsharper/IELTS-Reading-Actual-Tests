"""Authoring files (src/vol1-test-N.json) -> data/<volume>.json for build-html.mjs.

Usage: python -X utf8 -I _generator/build_data.py src/vol1 data/vol-1.json "IELTS Reading Recent Actual Tests – Vol 1" vol-1
See _generator/FORMAT.md for the authoring format. Fails loudly on anything it cannot place.
"""
import json, re, sys, os, glob

NUMWORD = {1: 'ONE', 2: 'TWO', 3: 'THREE', 4: 'FOUR'}


def runs(text):
    """Inline markup -> runs: **bold**, *italic*, __underline__, [[n]] gaps, [[n:2]] second blank, [[img:name]] picture."""
    out = []
    pos = 0
    pat = re.compile(r'(\*\*.+?\*\*|__.+?__|\*.+?\*|\[\[[^\]]+\]\])')
    for m in pat.finditer(text):
        if m.start() > pos:
            out.append({'t': text[pos:m.start()]})
        tok = m.group(0)
        if tok.startswith('**'):
            out.append({'t': tok[2:-2], 'b': True})
        elif tok.startswith('__'):
            out.append({'t': tok[2:-2], 'u': True})
        elif tok.startswith('[['):
            inner = tok[2:-2]
            if inner.startswith('img:'):
                out.append({'img': inner[4:]})
            elif ':' in inner:
                n, part = inner.split(':')
                out.append({'gap': int(n), 'part': int(part)})
            else:
                out.append({'gap': int(inner)})
        else:
            out.append({'t': tok[1:-1], 'i': True})
        pos = m.end()
    if pos < len(text):
        out.append({'t': text[pos:]})
    return out or [{'t': ''}]


def para(text, center=False):
    b = {'type': 'p', 'runs': runs(text)}
    if center:
        b['center'] = True
    return b


def blocks_from(items):
    """content/intro items: str paragraph, {'center': str}, {'table': [[cell,...],...], 'header': bool}, {'h': str}."""
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(para(it))
        elif 'center' in it:
            out.append(para(it['center'], True))
        elif 'h' in it:
            out.append({'type': 'h', 'runs': runs(it['h'])})
        elif 'table' in it:
            rows = [[[para(c)] if c != '' else [] for c in row] for row in it['table']]
            out.append({'type': 'table', 'rows': rows})
        else:
            raise SystemExit('unknown content item %r' % (it,))
    return out


def limit_of(spec):
    if not spec:
        return None
    words = spec['words']
    num = bool(spec.get('number'))
    text = NUMWORD[words] + (' WORDS' if words > 1 else ' WORD')
    if num:
        text += ' AND/OR A NUMBER'
    return {'words': words, 'number': num, 'text': text}


def accept_list(v):
    if isinstance(v, list):
        return v
    return [v]


def build_group(g, key):
    a, b = g['range']
    nums = list(range(a, b + 1))
    title = g.get('title') or ('Questions %d–%d' % (a, b) if b > a else 'Question %d' % a)
    out = {'type': g['type'], 'title': title, 'numbers': nums, 'intro': blocks_from(g.get('intro', []))}
    t = g['type']
    ans = g.get('answers', {})  # {"n": "X" | ["X","alt"]}
    alt = g.get('alsoAccept', {})

    def setkey(n, v):
        lst = accept_list(v)
        if t in ('tfng', 'ynng'):
            lst = [x.upper() for x in lst]
        key[n] = {'answer': lst[0], 'accept': lst, 'explanation': [], 'evidence': None}
        if str(n) in alt:
            key[n]['accept'] = lst + [x for x in alt[str(n)] if x not in lst]

    if t in ('tfng', 'ynng'):
        out['choices'] = ['TRUE', 'FALSE', 'NOT GIVEN'] if t == 'tfng' else ['YES', 'NO', 'NOT GIVEN']
        out['questions'] = [{'n': n, 'stem': runs(g['items'][str(n)])} for n in nums]
    elif t == 'short':
        out['questions'] = [{'n': n, 'stem': runs(g['items'][str(n)])} for n in nums]
        out['limit'] = limit_of(g['limit'])
    elif t == 'mcq':
        out['questions'] = []
        for n in nums:
            it = g['items'][str(n)]
            out['questions'].append({'n': n, 'stem': runs(it['stem']), 'options': [{'key': k, 'runs': runs(v)} for k, v in it['options'].items()]})
    elif t == 'multi':
        out['label'] = '%d-%d' % (a, b)
        out['stem'] = runs(g['stem'])
        out['choose'] = g['choose']
        out['options'] = [{'key': k, 'runs': runs(v)} for k, v in g['options'].items()]
        letters = [x.strip() for x in re.split(r'[,\s]+', g['answer']) if x.strip()]
        assert len(letters) == g['choose'], g
        out['key'] = {'answer': ', '.join(letters), 'accept': letters, 'explanation': [], 'evidence': None}
        for n in nums:
            pass  # answers live in out['key']
        return out, True
    elif t in ('match', 'grid', 'headings'):
        if 'options' in g:
            o = g['options']
            out['options'] = {'title': [runs(x) for x in o['title']] if o.get('title') else None,
                              'list': [{'key': k, 'runs': runs(v)} for k, v in o['list'].items()]}
            out['optionsAfter'] = bool(o.get('after'))
            out['type'] = 'match' if t == 'grid' else t
        else:
            out['letters'] = g['letters']  # e.g. ["A","B",...]
            out['type'] = 'grid'
        out['questions'] = [{'n': n, 'stem': runs(g['items'][str(n)]) if g['items'].get(str(n)) else None} for n in nums]
        if out['type'] == 'headings':
            pass
    elif t in ('gap', 'bank'):
        out['content'] = blocks_from(g['content'])
        if t == 'bank':
            o = g['options']
            out['options'] = {'title': [runs(x) for x in o['title']] if o.get('title') else None,
                              'list': [{'key': k, 'runs': runs(v)} for k, v in o['list'].items()]}
            out['optionsAfter'] = bool(o.get('after'))
        else:
            out['limit'] = limit_of(g.get('limit'))
            if g.get('after'):
                out['after'] = blocks_from(g['after'])
            if g.get('imageAlt'):
                out['imageAlt'] = g['imageAlt']
        if g.get('pairs'):
            out['pairs'] = g['pairs']
        if out.get('limit') is None:
            out.pop('limit', None)
    else:
        raise SystemExit('unknown group type ' + t)

    for n in nums:
        if str(n) not in ans:
            raise SystemExit('no answer for question %d' % n)
        setkey(n, ans[str(n)])
    for x, y in g.get('unordered', []):
        both = [accept_list(ans[str(x)])[0], accept_list(ans[str(y)])[0]]
        key[x] = {**key[x], 'accept': both, 'unordered': {'with': y, 'second': False}}
        key[y] = {**key[y], 'accept': [both[1], both[0]], 'unordered': {'with': x, 'second': True}}
    return out, False


def build_passage(test, p, order):
    key = {}
    groups = []
    for g in p['groups']:
        grp, is_multi = build_group(g, key)
        groups.append(grp)
    body = []
    for para_ in p['paragraphs']:
        if isinstance(para_, str):
            body.append({'runs': runs(para_)})
        elif 'sub' in para_:
            body.append({'sub': True, 'runs': runs(para_['sub'])})
        else:
            body.append({'letter': para_['l'], 'runs': runs(para_['t'])})
    slug = 'passage-t%d-p%d-%s' % (test, p['n'], re.sub(r'[^a-z0-9]+', '-', p['title'].lower()).strip('-'))
    return {
        'slug': slug, 'order': order, 'number': p['n'], 'label': 'Test %d · Passage %d' % (test, p['n']),
        'group': 'Test %d' % test,
        'head': [para(x) for x in p.get('head', [])],
        'title': [{'t': p['title'], 'b': True}],
        'standfirst': {'runs': runs(p['standfirst'])} if p.get('standfirst') else None,
        'body': body,
        'footnotes': [para(x) for x in p.get('footnotes', [])],
        'groups': groups,
        'key': key,
        'strategy': [], 'reading': [],
    }


def main(src, out, topic, slug):
    files = sorted(glob.glob(os.path.join(src, '*.json')), key=lambda f: int(re.search(r'test-(\d+)', f).group(1)))
    passages = []
    groups = []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        groups.append('Test %d' % d['test'])
        for p in d['passages']:
            passages.append(build_passage(d['test'], p, len(passages) + 1))
    data = {'topic': topic, 'slug': slug, 'numberLabel': 'Passage', 'groups': groups, 'topicNotes': None, 'sources': [], 'passages': passages}
    # the builder wants each group's keys of key as strings and group.key for multi
    for p in passages:
        for g in p['groups']:
            pass
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print('%d passages -> %s' % (len(passages), out))


if __name__ == '__main__':
    main(*sys.argv[1:5])
