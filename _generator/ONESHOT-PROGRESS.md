# One-shot guides – progress (Actual Tests)

2026-11-25: every passage (vol-1 24, vol-2 18, vol-3 9, practice-1 18 = 69) has a "Hướng dẫn One-Shot" (`strategy`).

## Tooling
- `python _generator/oneshot-dump.py <topic> <slug>` prints a passage with paragraph numbers, questions and key (`--list` lists slugs).
- Guide source: `_generator/strategy/<topic>/<slug>.json` (schema as in the IELTS-Reading-Passages repo).
- `node _generator/oneshot-apply.mjs <topic> --check` validates (answers = key, quotes occur in passage, every key question covered, no answers for questions missing from the key).
- `node _generator/oneshot-apply.mjs <topic>` writes `strategy` into `data/<topic>.json`; then `node _generator/build-html.mjs`.
- IMPORTANT: `build_data.py` (from `src/`) sets `strategy: []`, so after any data rebuild re-run the apply script for all four topics, then build-html.
- Some data files have keys only up to a certain question (e.g. vol-2 t1-p2 Q24–26, practice-1 t1-p3 Q39–40); guides cover only questions that have a key.
