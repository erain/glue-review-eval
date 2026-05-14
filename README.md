# glue-review-eval

Benchmark + harness for the [glue-review](https://github.com/erain/glue/tree/main/agents/glue-review) code-review agent.

## Why

`glue-review` is being polished into a single-purpose tool: produce **one GitHub comment per PR, optimized for AI coding agents to consume** — short human-readable summary on top, copy-pasteable markdown fix-instruction block on the bottom. This repo is the test bed we measure against while we iterate the prompt and template.

## Layout

```
hosts/                      # three realistic host projects, baseline-green
  go-glog/                  # Go: structured-log tail/filter CLI
  python-linkr/             # Python: FastAPI URL shortener
  ts-notepad/               # TS: Vite + React markdown notepad

cases/                      # per-PR scenarios applied against the hosts
  <lang>/<case-id>/
    case.yaml               # ground-truth sidecar (planted bug, expected fix, acceptance test)
    patch.diff              # the PR's diff against the host's baseline
    README.md               # what this case is testing and why

harness/
  runner/                   # invokes glue-review against each case, captures output
  judge/                    # LLM-as-judge scorer using ground truth from case.yaml
  scorer/                   # Layer 1 structural recall + aggregation

results/                    # per-iteration scorecards + raw outputs (gitignored except for summaries)
prompts-snapshots/          # frozen copies of agent prompts at each iteration
docs/                       # design docs: SIDECAR.md, OUTPUT_FORMAT.md, METRICS.md
```

## The three-layer eval stack

| Layer | What it measures | Cost | Cadence |
|------:|------------------|------|---------|
| 1 | Structural recall: did the comment mention the planted file/line? | ~free | every iteration |
| 2 | LLM-as-judge rubric (0–10 on identify / specificity / severity / conciseness / false-positives) using planted-bug ground truth | ~1¢ / case | every iteration |
| 3 | Downstream fix-success: hand the fix block to a real coding agent (codex / opencode / claude headless), check if the planted acceptance test goes red→green | ~5–10¢ / case | every 5 iterations on a 5-case subset |

## Status

See [PROGRESS.md](./PROGRESS.md) for the current iteration log.
