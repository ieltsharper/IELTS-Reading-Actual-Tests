// Loads every generated passage page with the real assets/reading.js (jsdom) and checks the marking:
// key answers score N/N, every accepted alternative scores N/N, an empty page scores 0, and every question
// answered wrongly on its own scores N-1. Also checks inputs, feedback boxes, the navigator and the images.
// Usage: node _generator/check_pages.mjs [vol-1]   (jsdom from the portal, or set JSDOM_PATH)
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const slug = process.argv[2] || 'vol-1';
const jsdomPath = process.env.JSDOM_PATH || 'D:/IELTS LEARNING PORTAL/node_modules/jsdom';
const { JSDOM } = createRequire(import.meta.url)(jsdomPath);
const data = JSON.parse(fs.readFileSync(path.join(root, 'data', `${slug}.json`), 'utf8'));
const readingJs = fs.readFileSync(path.join(root, 'assets', 'reading.js'), 'utf8');
const bad = [];
const ok = (c, m) => {
  if (!c) bad.push(m);
};
const listKind = (q) => q.kind === 'multi' || q.kind === 'pair';
const answers = (q) => (listKind(q) ? q.accept : q.accept[0]);

for (const p of data.passages) {
  const file = path.join(root, slug, `${p.slug}.html`);
  const label = p.label;
  if (!fs.existsSync(file)) {
    bad.push(`${label}: page ${file} missing`);
    continue;
  }
  const html = fs.readFileSync(file, 'utf8');
  const url = `http://localhost/${slug}/${p.slug}.html`;
  const dom = new JSDOM(html, { url, runScripts: 'outside-only' });
  dom.window.confirm = () => true;
  dom.window.HTMLElement.prototype.scrollIntoView = () => {};
  dom.window.eval(readingJs);
  const r = dom.window.__reading;
  const doc = dom.window.document;
  if (!r) {
    bad.push(`${label}: reading.js did not start`);
    continue;
  }
  const qs = r.data.questions;
  const N = r.data.total;
  const expectedN = p.groups.reduce((s, g) => s + g.numbers.length, 0);
  ok(N === expectedN, `${label}: page has ${N} questions, data ${expectedN}`);
  ok(/noindex/.test(html), `${label}: no noindex`);
  ok(!/https?:\/\/(?!script\.google|script\.googleusercontent)/.test(html.replace(/<a [^>]*>/g, '').replace(/<meta[^>]*>/g, '')), `${label}: loads from another site`);
  for (const m of html.matchAll(/(?:src|href)="(\.\.?\/[^"#]+)"/g)) {
    ok(fs.existsSync(path.join(path.dirname(file), m[1])), `${label}: broken link ${m[1]}`);
  }
  const navs = [...doc.querySelectorAll('.q-nav [data-nav]')].map((a) => +a.textContent);
  ok(navs.length === N, `${label}: navigator has ${navs.length} buttons, ${N} questions`);
  for (const q of qs) {
    ok(doc.querySelectorAll(`[data-q="${q.id}"]`).length > 0, `${label}: no input for ${q.id}`);
    ok(doc.getElementById(`fb-${q.id}`), `${label}: no feedback box for ${q.id}`);
    ok(q.accept.length > 0 && q.accept.every((a) => String(a).trim()), `${label}: empty answer for ${q.id}`);
  }
  const run = (fill) => {
    for (const q of qs) r.setValue(q, fill(q));
    r.check();
    return +doc.getElementById('score').textContent.match(/Score: (\d+)/)[1];
  };
  ok(run(answers) === N, `${label}: key answers do not score ${N}/${N}`);
  const maxAlt = Math.max(...qs.map((q) => (listKind(q) ? 1 : q.accept.length)));
  for (let k = 1; k < maxAlt; k++) {
    ok(run((q) => (listKind(q) ? q.accept : q.accept[Math.min(k, q.accept.length - 1)])) === N, `${label}: alternative #${k} does not score ${N}/${N}`);
  }
  ok(run((q) => (q.kind === 'text' ? `  ${q.accept[0].toUpperCase().replace(/'/g, '\u2019')}. ` : answers(q))) === N, `${label}: case/spacing variants fail`);
  ok(run(() => '') === 0 && run((q) => (q.kind === 'multi' ? [] : '')) === 0, `${label}: empty page does not score 0`);
  const wrongFor = (q) =>
    q.kind === 'text'
      ? 'zzz'
      : q.kind === 'pair'
        ? ['zzz', 'zzz']
        : [...doc.querySelectorAll(`[data-q="${q.id}"]`)].flatMap((e) => (e.tagName === 'SELECT' ? [...e.options].map((o) => o.value) : [e.value])).find((v) => v && !q.accept.includes(v));
  for (const q of qs) {
    if (q.kind === 'multi') {
      const wrongLetter = [...doc.querySelectorAll(`[data-q="${q.id}"]`)].map((e) => e.value).find((v) => !q.accept.includes(v));
      const s = run((x) => (x.id === q.id ? [...q.accept.slice(1), wrongLetter] : answers(x)));
      ok(s === N - 1, `${label}: ${q.id} with one wrong letter scores ${s}`);
    } else {
      const w = wrongFor(q) ?? 'zzz';
      const s = run((x) => (x.id === q.id ? w : answers(x)));
      ok(s === N - 1, `${label}: ${q.id} wrong still scores ${s}/${N}`);
    }
  }
  console.log(`${label}: ${N} questions, ${maxAlt > 1 ? 'alternatives' : 'no alternatives'}, checked`);
}
for (const b of bad) console.log('PROBLEM:', b);
console.log(bad.length ? `${bad.length} problems` : 'OK');
process.exit(bad.length ? 1 : 0);
