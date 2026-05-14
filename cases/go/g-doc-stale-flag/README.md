# g-doc-stale-flag

**Category:** doc · **Severity:** low · **Host:** go-glog

A README-only PR renames the time-window flags from `--since`/`--until`
to `--within`/`--before` "for readability". No code change accompanies
it. `cmd/glog/main.go` still wires only `--since` and `--until`, so the
new names don't exist and anyone copying the example from the README
gets `flag provided but not defined`.

The reviewer should flag the README diverging from the actual CLI
surface. Acceptance is a grep over `README.md` for the original
`--since` / `--until` names — the cleanest fix is a revert, though a
thorough fix could add `--within` / `--before` as aliases in
`main.go`. The grep gate accepts only the doc-side fix to keep the
test deterministic; either fix is fine in practice.
