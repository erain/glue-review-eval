# g-ignored-unmarshal-err

**Category:** logic-bug · **Severity:** medium · **Host:** go-glog

`entry.Parse` is rewritten as "tolerant": the early-return that rejects
non-`{` input and the early-return on `json.Unmarshal` error are both
removed. The Unmarshal error is assigned to `_` and `Parsed` is set to
`true` unconditionally. The PR justifies the change as supporting
syslog-prefixed lines.

The fallout: `Parsed` no longer means "this decoded as JSON", which is
exactly the signal `filter.Match` uses to short-circuit any predicate
that needs structured data. Lines that previously failed `--level` or
`--field` because they were unparsed now slip past that guard and are
only rejected because their (zero) `Level` / `HasTS` happen to not match.
Any future filter that doesn't have a zero-value escape hatch will
quietly misbehave on invalid JSON.

`TestParse_RawPassthrough` was edited in the same PR to assert
`Fields == nil` rather than `Parsed == false`, which masks the
regression. The reviewer should call out both the ignored Unmarshal
error and the suspicious weakening of the existing test.

`TestParse_InvalidJSONIsUnparsed` is the acceptance gate: it calls
`Parse("not json")` and asserts `Parsed == false`. Buggy code reports
`true`.
