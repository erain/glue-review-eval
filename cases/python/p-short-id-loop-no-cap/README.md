# p-short-id-loop-no-cap

**Category:** logic-bug · **Severity:** medium · **Host:** python-linkr

`generate_unique_short_id` had an 8-attempt cap; this PR loosens it to
`max_attempts: int | None = None` with the new default being unbounded.
The justification reads plausibly — 62^6 is 57 billion slots and the
`exists` callback is a cheap SQLite query — but the live caller in
`app/routes.py` passes no `max_attempts`, so any pathological `exists`
(misconfigured soft-delete filter, broken test fake, transient DB issue
that misreports rows as taken) wedges a worker thread forever inside
`while True:`.

The acceptance test runs the generator on a background thread with
`exists=lambda _c: True` and joins for 2 seconds. Planted code: thread
stays alive, test fails. Bounded fix: `ShortIDCollision` raises almost
instantly and the test passes.

A reasonable reviewer should reject the unbounded default and ask for
either a restored finite cap or — if unboundedness is genuinely wanted
— an explicit caller opt-in (`max_attempts=None` only when the caller
passes it, not as the implicit default).
