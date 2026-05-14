# p-test-only

**Category:** test-only · **Severity:** none · **Host:** python-linkr

Four new tests in `tests/test_health_shape.py` pin down the `/healthz`
JSON contract: content-type, exact set of keys, value, and idempotence
across successive calls. No production code changes — this is a pure
coverage uplift PR.

All 26 existing tests still pass; with the new ones, the suite is 30.

This is a false-positive probe like `p-clean-typing`. The reviewer
should approve or at most nitpick. The `must_not_flag` list guards
against the reviewer claiming the tests encode a regression, introduce
something unsafe, or constitute a breaking change.
