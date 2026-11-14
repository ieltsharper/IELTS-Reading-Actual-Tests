# Authoring format: src/vol1/test-N.json

One file per test. A worked example (Test 1, Passage 1: headings, TFNG, choose-three) is in `src/vol1/test-1.json`.
Convert + build + check:

    python -X utf8 -I _generator/build_data.py src/vol1 data/vol-1.json "Recent Actual Tests – Vol 1" vol-1
    node _generator/build-html.mjs
    python -X utf8 -I _generator/check_data.py data/vol-1.json

## Source material (the book "IELTS Reading Recent Actual Tests Vol 1", scanned, image only)

- Page pictures: `D:/HarperSites/_scratch/vol1/png/pNNN.png` (200 dpi, 1653x2339).
- Windows-OCR draft text: `D:/HarperSites/_scratch/vol1/ocr/pNNN.txt` — has many small errors and DROPS words.
  `python -X utf8 -I _generator/ocr_clean.py D:/HarperSites/_scratch/vol1/ocr FIRST LAST` prints a cleaned draft
  (watermark lines removed, "Th" ligature errors like `%ough` repaired, unknown words wrapped in «…»).
- Page map: Test 1 = pp 3-15, Test 2 = 16-29, Test 3 = 30-42, Test 4 = 43-58, Test 5 = 59-72, Test 6 = 73-88,
  Test 7 = 89-101, Test 8 = 102-117 (each: passage 1, 2, 3, each followed by its question pages).
  Answer keys: pp 118-125 (Test 1 = 118 … Test 8 = 125). Read the key from the PICTURE (the OCR scrambles columns).
- Page numbers in the book differ from PDF pages by 2 (PDF page 5 = book page 7).

## Faithfulness rules (the owner's rules)

1. The OCR is only a draft. **Look at every page picture** and compare line by line; fix wrong letters
   (e.g. `thcorics` → `theories`, `(&een` → `Queen`, `l` for `I`), restore words the OCR dropped (check the first
   word of paragraphs — drop caps are often lost: "A rlhe" = "The"), restore italics (`*Odyssey*`),
   paragraph breaks, headings, and numbers/dates exactly as printed.
2. Keep the book's own wording, spelling and (British) style, even odd phrasing. Do not correct the source,
   do not paraphrase, do not add explanations. Where the book looks wrong, keep it and list it in your report.
3. Join words hyphenated only by line breaks (`magnet-` / `ism` → `magnetism`); keep real hyphens (`pre-dated`).
4. Typographic quotes as printed: ’ for the apostrophe, “ ” for double quotes.
5. Drop only: the watermark lines (www.i-educator.vn, www.facebook.com/ieducatorvn), the running header
   “IELTS Reading Recent Actual Tests”, and page numbers/“Test N” corner labels.
6. Question numbers must be exactly 1-40 across the three passages, as printed (usually 1-13, 14-26, 27-40).
7. Answers come from the key page(s) 118-125 (read the picture). `True/False/Not Given` and `Yes/No/Not Given` are
   normalised to capitals by the converter. Keep the key's spelling, e.g. `2000 floods / flooding` means two accepted
   forms: write `["2000 floods", "2000 flooding"]`; `1976, 1995` for a single question stays one string. If the key
   shows alternatives with `/` or `or`, give them as a list (first = the one displayed).
8. A diagram / map / flow-chart / picture that cannot be typed (map, labelled diagram) is cut from the page
   picture with `python -X utf8 -I _generator/crop.py PAGE x0 y0 x1 y1 NAME` (fractions 0-1 of the page) and used
   as `[[img:NAME]]` inside a `gap` group's content; its answers still use the normal text-box format. Tables and
   flow-charts MUST be typed (see "table"), not pictures, unless they are truly graphical.

## File layout

```json
{ "test": 1,
  "passages": [ { "n": 1, "title": "…", "head": ["optional line above the title"], "standfirst": "optional line under title",
                  "paragraphs": [ {"l": "A", "t": "text with *italic* **bold** __underline__"}, {"sub": "Section heading"}, "plain paragraph" ],
                  "footnotes": ["optional glossary line"],
                  "groups": [ … ] } ] }
```

Use `{"l": "A", …}` for lettered paragraphs/sections (also when the book prints "Section A"). Passages without letters
use plain strings. If a passage has a box or picture inside the text, describe what you could not type in your report.

## Question groups (`groups`), always `"range": [first, last]`, `"intro": ["line", …]` (the printed instructions, verbatim, one string per paragraph)

| type | extra fields |
|---|---|
| `tfng` / `ynng` | `items: {"8": "statement"}`, `answers: {"8": "True"}` |
| `short` | `items: {"6": "question"}`, `limit: {"words": 2, "number": false}` (number true = "AND/OR A NUMBER"), `answers` |
| `mcq` | `items: {"14": {"stem": "…", "options": {"A": "…", "B": "…"}}}`, `answers: {"14": "C"}` |
| `multi` (choose two/three letters; range spans all its questions) | `choose: 3`, `stem`, `options: {"A": "…"}`, `answer: "C, D, E"` (no `answers`) |
| `headings` / `match` (options list shown) | `options: {"title": ["**List of Headings**"], "list": {"i": "…"}, "after": false}`, `items: {"1": "Paragraph **A**"}` (for `match`: the statement/person to match), `answers`. For headings whose items are page-printed “Paragraph A”, items hold that text |
| `grid` (match to paragraph letters, no list) | `letters: ["A","B","C","D","E","F","G","H"]`, `items: {"27": "statement"}`, `answers` |
| `gap` (notes / summary / sentences / table / flow-chart with typed answers) | `content: [ … ]`, `limit`, `answers`; optional `after: [ … ]`, `pairs`, `unordered: [[21, 22]]` (two answers that may come in either order) |
| `bank` (fill gaps from a lettered word box) | `content`, `options: {"title": [..] or null, "list": {"A": "word"}}`, `answers: {"9": "C"}` |

`content` items: a string paragraph with gaps written `[[9]]` (second blank of the same question: `[[9:2]]`),
`{"center": "Title line"}`, `{"h": "Heading"}`, or a table `{"table": [["Header1","Header2"],["cell [[14]]","cell"]]}`
(all cells are strings; an empty cell is `""`). A flow-chart: one paragraph per box in reading order, with an arrow
paragraph `↓` between boxes. Sentence-completion lists: one string per sentence.
Wherever the book puts the gap inline in a sentence, put `[[n]]` in the same place; keep the words around it exactly.
The number of the question always appears as `[[n]]`, never as printed digits in the text.

Optional `alsoAccept: {"7": ["alt answer"]}` per group for extra accepted forms the book's key did not list: do NOT add
any; report suspected extra forms instead.

## Done means

`build_data.py` and `check_data.py` pass for your test, and every page picture of your test was compared with your text.

## Vol 2 ("IELTS READING Recent Actual tests Vol 2.pdf", photographed book, image only, 7 tests)

Same rules and format as above, with these differences:

- Page pictures: `D:/HarperSites/_scratch/vol2/png/pNNN.png`; OCR drafts: `D:/HarperSites/_scratch/vol2/ocr/pNNN.txt`
  (`ocr_clean.py D:/HarperSites/_scratch/vol2/ocr FIRST LAST`). The pages are photographs: shadows, curved text, so the OCR is
  poorer than Vol 1; trust the picture.
- Page map (PDF pages): Test 1 = 15-30, Test 2 = 31-42, Test 3 = 43-54, Test 4 = 55-67, Test 5 = 68-79, Test 6 = 80-90,
  Test 7 = 91-102. Answer keys: pp 190-196 (Test 1 = 190 ... Test 7 = 196), read from the picture.
- Pages 103-189 are a Chinese "真题解析" analysis of the same tests: ignore them entirely. Do not type Chinese.
- Files go in `src/vol2/test-N.json`. Build: `python -X utf8 -I _generator/build_data.py src/vol2 data/vol-2.json "Recent Actual Tests – Vol 2" vol-2`
  (the main session builds; you only need `check_data.py` on your own test: it takes `data/vol-2.json` after a build, so first
  run build_data into a scratch file: `... build_data.py <dir containing only your test file> /tmp/vol2-tN.json "x" vol-2`).
- Crops: `crop.py PAGE x0 y0 x1 y1 NAME vol-2` (the last argument is needed).

## Volumes 3-6 (same pipeline; scratch pictures and OCR drafts per volume)

Pictures `D:/HarperSites/_scratch/volN/png/pNNN.png` (N = 3..6, width 1654 px), OCR drafts `.../volN/ocr/pNNN.txt`
(`ocr_clean.py D:/HarperSites/_scratch/volN/ocr FIRST LAST`). Files go in `src/volN/test-T.json`; crops: `crop.py PAGE x0 y0 x1 y1 tT-NAME vol-N`.
Pages other than the ones listed are a Chinese analysis, covers or blank: ignore them. All are image-only PDFs; trust the picture.

| Volume | PDF pages per test | Answer keys (PDF pages) |
|---|---|---|
| Vol 3 | T1 22-33, T2 34-46, T3 47-58, T4 59-70, T5 71-82, T6 83-95 | 260 = T1 ... 265 = T6 |
| Vol 4 | T1 2-15, T2 16-29, T3 30-44, T4 45-59, T5 60-74, T6 75-89 | 90 = T1 ... 95 = T6 |
| Vol 5 | T1 3-17, T2 18-33, T3 34-47, T4 48-61, T5 62-78, T6 79-94 | 285 = T1 ... 290 = T6 |
| Vol 6 | T1 2-14, T2 15-30, T3 31-44, T4 45-58, T5 59-73, T6 74-88 | 89 = T1 ... 94 = T6 |

(Boundaries come from the OCR: if the first or last page of a test is slightly off, follow the pictures; key pages may hold
one test or two: check the 'Test N' headings in the picture.) Some key pages may print passage-1/2/3 columns in a different
order from the page text: map every answer by its printed question number.
