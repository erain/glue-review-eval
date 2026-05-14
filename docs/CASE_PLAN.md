# Case plan (v1)

~9 cases per host, ~27 total. Each row maps a case directory under
`cases/<lang>/<id>/` to a planted-bug intent. Patches authored once host
projects land; this doc is the contract for what each case must exercise.

## Severity vocabulary

`critical` | `high` | `medium` | `low` | `nit` (and `none` for clean PRs).

## python-linkr cases

| id | category | severity | what we plant |
|----|----------|----------|---------------|
| `p-sql-injection-stats` | security | critical | `routes.py` builds raw SQL with `f"... WHERE short_id = '{short_id}'"` for a new "GET /links/{short_id}/stats" endpoint |
| `p-missing-auth-delete` | security | high | DELETE endpoint added without `Depends(require_api_key)` |
| `p-mutable-default-arg` | logic-bug | medium | helper added with `def f(tags=[]):` (classic Python footgun) |
| `p-short-id-loop-no-cap` | logic-bug | medium | `shortener.py` retry loop changed from bounded to `while True:` (potential infinite loop under saturation) |
| `p-clean-typing` | clean | none | adds type hints to private helpers and a few docstrings; no behavior change |
| `p-doc-url-mismatch` | doc | low | README still says `POST /shorten`, code already says `POST /links` — README never updated |
| `p-rejected-globals` | rejected-direction | high | introduces a module-level `_engine` and `_session` to "simplify", abandoning dependency injection |
| `p-multi-auth-and-test` | multi-bug | high | adds an endpoint, missing auth + missing test (two independent issues in one PR) |
| `p-test-only` | test-only | none | only adds tests for existing GET /healthz behaviour |

## go-glog cases

| id | category | severity | what we plant |
|----|----------|----------|---------------|
| `g-off-by-one-bound` | logic-bug | high | filter loop iterates `i <= len(xs)`, index-out-of-bounds on non-empty input |
| `g-ignored-unmarshal-err` | logic-bug | medium | `entry.go` swallows `json.Unmarshal` error; affected paths treat raw line as parsed |
| `g-leaked-file-handle` | logic-bug | medium | `tail.go --follow` path opens file but never closes on graceful shutdown |
| `g-style-export-name` | style | nit | new helper exported as `filtermatch` (lowercased) — package-level naming inconsistent |
| `g-missing-flag-test` | missing-test | medium | new `--out json` mode added without a corresponding test |
| `g-clean-extract` | clean | none | pure refactor: extracts a `lineSplit` helper, behavior unchanged |
| `g-rejected-package-mutable` | rejected-direction | high | introduces a `var GlobalFilter *Filter` populated from main, mutated from tests |
| `g-doc-stale-flag` | doc | low | README example shows old `--since`, code has new `--within` (or vice versa) |
| `g-multi-render-and-test` | multi-bug | high | bug in `render.plain` (drops a field) + no test for the new path |

## ts-notepad cases

| id | category | severity | what we plant |
|----|----------|----------|---------------|
| `t-xss-skip-sanitize` | security | critical | `markdown.ts` removes `DOMPurify.sanitize` and renders marked HTML directly |
| `t-stale-closure-effect` | logic-bug | high | `useEffect` captures stale state without a dependency entry, write loses the latest edit |
| `t-debounce-removed` | perf | medium | autosave loses its `useDebounce` wrap — fires on every keystroke into localStorage |
| `t-list-missing-key` | style | medium | NoteList maps without `key` prop (React warning surface) |
| `t-missing-shortcut-test` | missing-test | medium | new `Cmd+N` shortcut added without test |
| `t-clean-theme-hook` | clean | none | extracts a `useColorScheme` hook from inline code; no behavior change |
| `t-rejected-context-everything` | rejected-direction | medium | introduces a global `NotesContext` for state that the hooks already handle |
| `t-any-types-creep` | style | low | sprinkle `any` types in non-trivial spots, replacing real types |
| `t-multi-effect-and-leak` | multi-bug | high | missing dependency array in `useEffect` + a `setTimeout` never cleared |

## Authoring order

Each case is a directory:

```
cases/<lang>/<id>/
  case.yaml          # ground truth sidecar (see docs/SIDECAR.md)
  patch.diff         # unified diff applied on top of hosts/<host>'s baseline
  README.md          # 1-paragraph note for humans skimming the case
```

We author cases in this order so that the harness can be wired and
sanity-checked against real cases as early as possible:

1. **python-linkr first** (host is already shipped): `p-sql-injection-stats`,
   `p-missing-auth-delete`, `p-clean-typing`. Three cases is enough to
   exercise security / clean / and a third category. Run the harness
   end-to-end against these to find bugs in the runner / scorer / judge.
2. Then fill in the remaining linkr cases, then go-glog, then ts-notepad
   as those hosts land.
3. Final sanity at the end of Phase 2: run all ~27 against the current
   glue-review (Phase 3 baseline).
