# g-clean-extract

**Category:** clean · **Severity:** none · **Host:** go-glog

A pure refactor: the reserved-key filter loop inside `plain.Render` is
extracted into a small `nonReservedKeys(e entry.Entry) []string`
helper. The render function reads more linearly afterwards. No
behaviour change; every existing test passes.

This case checks the reviewer's false-positive resistance. It should
approve (or at most leave a tiny taste-level nudge) and must not
invent off-by-one, missing-test coverage demands (the helper is
exercised by every existing plain-render test), or thread-safety
concerns. No acceptance gate.
