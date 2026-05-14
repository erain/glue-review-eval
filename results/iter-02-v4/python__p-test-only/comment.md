## glue-review

No concerns — LGTM.

New test file adds valuable contract coverage for the `/healthz` response shape (content-type, exact field set, idempotence) without duplicating existing tests in `test_health.py`. Style is consistent with the project.
