# p-mutable-default-arg

**Category:** logic-bug · **Severity:** medium · **Host:** python-linkr

The classic Python footgun: a function argument whose default is a fresh
mutable list literal. `generate_unique_short_id` grows a new `tried`
parameter so callers can inspect which short IDs were rolled before a
free one landed — but the default is `tried: list[str] = []`, which is a
single list created at module-import time and reused on every call.

Every call without an explicit `tried` mutates the *same* list. The
process-wide accumulator grows without bound and leaks state across
unrelated requests.

The acceptance test (`tests/test_tried_default.py`) calls
`generate_unique_short_id` three times back-to-back without passing
`tried`, then inspects `generate_unique_short_id.__kwdefaults__["tried"]`.
With the planted code the default object has accumulated three
candidates; with the `None`-sentinel fix the default stays `None` and
the assertion passes via the early-return branch.

The reviewer should name the mutable-default pattern, point at
`app/shortener.py`, and suggest the `None` sentinel as the fix.
