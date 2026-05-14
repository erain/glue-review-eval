Let me check the existing codebase for the health endpoint and related tests.## Summary

Adds a new test file `tests/test_health_shape.py` with contract-level tests for the `/healthz` endpoint, covering JSON content-type, exact response shape (single `status` field), value correctness, and idempotence.

## Issues

No bugs or regressions found.

## Suggestions

- [minor] tests/test_health_shape.py:4 — The docstring says "`test_health.py` already covers status-code + status field" but the four tests here do overlap with assertions in `tests/test_health.py` (status code 200, `status == "ok"`, body shape). This is intentional per the docstring, but worth noting that any future rename or restructuring of the health endpoint would need to be kept in sync across both files. Consider adding a brief cross-reference (e.g., a comment or `see also`) linking to `test_health.py` so future maintainers know the relationship.

## Looks good

- Clear separation of concerns: existing `test_health.py` covers functional behavior (auth, status codes), new file contracts the JSON shape.
- Tests are well-written, idempotent, and use the existing `client` fixture correctly.
- Commit message is descriptive.

## Open questions

None.
