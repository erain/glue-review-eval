# Sidecar schema (`case.yaml`)

Every case in `cases/<lang>/<case-id>/` ships a `case.yaml` that is the
ground truth for all three eval layers. It tells the harness what the
reviewer *should* find, what the fix-instruction block *should* say, and
what test gates a downstream coding agent's fix.

The schema is intentionally small. Add fields only when an eval layer
actually consumes them — drift between schema and harness is the most
common rot vector for benchmarks like this.

## Fields

```yaml
id:            string   # stable case id (kebab-case), unique within a language
language:      enum     # go | python | typescript
host:          string   # which hosts/<dir> this case patches
category:      enum     # logic-bug | style | missing-test | security | perf |
                       # doc | refactor-only | rejected-direction | mixed |
                       # clean    # "clean" = no real issue planted
severity:      enum     # critical | high | medium | low | none
                       # ("none" only for clean cases — tests reviewer's
                       # false-positive resistance)
title:         string   # human-readable PR title (the reviewer sees this)
summary:       string   # 1–3 line PR description (the reviewer sees this)

# What we planted. Empty for category=clean.
planted:
  description: string   # 1-paragraph plain-English description of the bug
  files:                # list — multi-bug cases have multiple entries
    - path: string
      lines: [int, int]   # inclusive line range in the patched file
      kind:  string       # short tag, e.g. "off-by-one", "missing-context-check"

# What we expect the reviewer's comment to do.
expected:
  must_flag:     [string]  # substrings/regexes that should appear in the comment
  must_not_flag: [string]  # things the reviewer must NOT claim (false-positive guard)
  fix_directives: [string] # short directives the fix-instruction block should include
                          # (e.g. "use < not <=", "wrap stmt in defer rows.Close()")

# Acceptance gate for Layer 3 (downstream-fix-success).
# Empty for category=clean (nothing to fix) and category=rejected-direction
# (we judge by whether reviewer pushed back, not by code change).
acceptance:
  setup:    [string]   # shell commands to set up the host (e.g. "go mod tidy")
  test_cmd: string     # one shell command; exit 0 = fix accepted
  timeout_s: int       # default 120

# Optional notes for humans skimming the case directory.
notes: string
```

## Example

```yaml
id: off-by-one-range-bound
language: go
host: go-glog
category: logic-bug
severity: high
title: "filter: range over entries"
summary: |
  Adds a Filter helper to glog/filter that returns matching entries.
  Caller iterates with i <= len; should be i < len.

planted:
  description: |
    Filter() iterates `i := 0; i <= len(es); i++`, causing an
    index-out-of-bounds panic on any non-empty input.
  files:
    - path: filter/filter.go
      lines: [22, 28]
      kind: off-by-one

expected:
  must_flag:
    - "filter/filter.go"
    - "off-by-one|out of bounds|<=|index"
  must_not_flag:
    - "race"          # there's no concurrency in this PR — guard against
    - "memory leak"   #   reviewer's habit of grasping at common buzzwords
  fix_directives:
    - "change <= to < in the loop bound"
    - "add a test covering non-empty input"

acceptance:
  setup:
    - "cd hosts/go-glog && go mod download"
  test_cmd: "cd hosts/go-glog && go test ./filter/..."
  timeout_s: 60
```

## Field-by-field notes for case authors

- **`expected.must_flag`** uses Python `re.search` semantics, case-insensitive.
  Keep entries narrow — the temptation is to over-specify and bake the
  reviewer's *current* phrasing into the ground truth. Phrases the reviewer
  uses today will change as we iterate the prompt; mention concepts, not
  wording.
- **`expected.must_not_flag`** is where you catch hallucination. A planted
  off-by-one shouldn't make the reviewer rant about thread safety. List the
  three or four buzzwords this category of code most commonly attracts that
  *aren't* relevant here.
- **`fix_directives`** is what the markdown fix-block should tell a downstream
  coding agent to do. Keep each one verb-first and acceptance-checkable
  ("change X to Y", "add test for Z"), not principle-level
  ("be more careful with bounds").
- **`acceptance.test_cmd`** must be deterministic and self-contained. If a
  fix could plausibly take several shapes (e.g. "use a real type" vs. "use a
  generic"), the test should pass for any correct shape.

## Clean and rejected-direction cases

For `category: clean`, set `severity: none`, leave `planted` empty, set
`expected.must_not_flag` to the buzzwords the reviewer might invent, and
`expected.must_flag` to a small list of approvals (e.g. `"LGTM|no concerns"`).
No `acceptance` block.

For `category: rejected-direction`, the bug is architectural — the reviewer
should refuse the approach, not propose a per-line fix. Use
`expected.must_flag` to list the design-level red flags the reviewer should
name (e.g. `"global mutable state"`, `"sync over channel"`). Skip
`acceptance`.
