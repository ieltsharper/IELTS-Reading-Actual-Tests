"""Clean Windows-OCR text of the scanned book pages and flag words that need a look at the page image.

Usage: python -X utf8 -I _generator/ocr_clean.py <ocr dir> <first page> <last page> [vocab dir]
Prints, for every page, the text with: watermark/footer lines removed, "%ough"-type ligature errors fixed,
line-end hyphens joined when the joined word is a known word, and every unknown word wrapped in «…».
The output is a DRAFT: always compare with the page picture (png/pNNN.png) before using any text.
"""
import re, sys, os, glob, json, collections

FIX = [
    (r'%ough', 'Though'), (r'%is\b', 'This'), (r'%e\b', 'The'), (r'%ere\b', 'There'), (r'%ey\b', 'They'),
    (r'%ese\b', 'These'), (r'%en\b', 'Then'), (r'%at\b', 'That'), (r'%us\b', 'Thus'), (r'%rough', 'Through'),
    (r'\bF1his\b', 'This'), (r'\bIhe\b', 'The'), (r'\bIhey\b', 'They'), (r'\bIhis\b', 'This'),
    (r'\bIhere\b', 'There'), (r'\bIhese\b', 'These'), (r'\bIhat\b', 'That'),
]
DROP = re.compile(r'(i-educator|facebook\.com|^\s*IELTS Reading Recent Actual Tests\s*$|^\s*\d{1,3}\s*$)', re.I)


def vocab_from(dirs):
    words = collections.Counter()
    for d in dirs:
        for f in glob.glob(os.path.join(d, '*.json')):
            try:
                data = json.load(open(f, encoding='utf-8'))
            except Exception:
                continue
            txt = json.dumps(data, ensure_ascii=False)
            for w in re.findall(r"[A-Za-z][A-Za-z']+", txt):
                words[w.lower()] += 1
    return words


def main():
    ocr_dir, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    vdirs = sys.argv[4:] or ['D:/HarperSites/IELTS-Reading-Passages/data']
    known = vocab_from(vdirs)
    own = collections.Counter()
    for f in glob.glob(os.path.join(ocr_dir, 'p*.txt')):
        for w in re.findall(r"[A-Za-z][A-Za-z']+", open(f, encoding='utf-8').read()):
            own[w.lower()] += 1
    def ok(w):
        w = w.lower().strip("'")
        return w in known or own[w] >= 2 or len(w) <= 1
    for p in range(a, b + 1):
        lines = open(os.path.join(ocr_dir, 'p%03d.txt' % p), encoding='utf-8').read().split('\n')
        lines = [l for l in lines if not DROP.search(l)]
        text = '\n'.join(lines)
        for pat, rep in FIX:
            text = re.sub(pat, rep, text)
        # join hyphenated line ends
        def join(m):
            left, right = m.group(1), m.group(2)
            joined = left + right
            return joined if ok(joined) else left + '-' + right
        text = re.sub(r"([A-Za-z]+)-\n([a-z]+)", join, text)
        def flag(m):
            w = m.group(0)
            return w if ok(w) else '«' + w + '»'
        text = re.sub(r"[A-Za-z][A-Za-z']*", flag, text)
        print('=== page %d (png/p%03d.png) ===' % (p, p))
        print(text)


if __name__ == '__main__':
    main()
