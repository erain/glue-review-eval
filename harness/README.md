# Harness

Three top-level entry points; each reads cases from `../cases/` and writes
results to `../results/<iter>/`.

```
python -m harness.runner   --iter <name>            # run glue-review on every case
python -m harness.scorer   --iter <name>            # compute Layer 1 (structural)
python -m harness.judge    --iter <name>            # compute Layer 2 (LLM-as-judge)
python -m harness.runner   --iter <name> --layer3   # run Layer 3 on subset
python -m harness.report   --iter <name>            # render results/scorecard.{csv,md}
```

Layout:

```
harness/
  __init__.py
  cases.py            # discover + parse case.yaml files; produce Case dataclass
  runner.py           # invoke glue-review against each case, save comment.md
  scorer.py           # Layer 1: regex over comment.md vs case.yaml
  judge.py            # Layer 2: Sonnet 4.6 LLM-as-judge
  layer3.py           # Layer 3: downstream coding-agent fix-success
  report.py           # aggregate -> scorecard.csv / .md
  config.py           # env, paths, executor list, model pins
```

## Conventions

- Every entry point takes `--iter NAME` (e.g., `iter-00-baseline`,
  `iter-01-tighten-headline`). Results land in `results/<iter>/`.
- Outputs are committed under `results/<iter>/` — raw comments,
  per-case scores, the aggregated scorecard. CSV is the source of truth;
  Markdown is regenerated.
- Errors abort the iteration with a non-zero exit and a clear message. We
  do not silently skip cases — incomplete iterations are worse than no
  iteration.
