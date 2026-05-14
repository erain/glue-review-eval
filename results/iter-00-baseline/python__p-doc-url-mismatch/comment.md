The diff is a minimal, docs-only change. Let me check if the server code actually uses the new `/shorten` route to ensure consistency.The README now documents `/shorten` but the actual route handler in `app/routes.py` still registers the endpoint at `/links`. This is a mismatch.## Summary

The branch updates the README to rename the create-link endpoint from `POST /links` to `POST /shorten`, but the actual server code still registers the route at `/links`.

## Issues

- [critical] README.md:7 — Documentation says `POST /shorten` but the route handler in `app/routes.py:15` still registers the path as `/links`. Users following the README will get 404s. Fix: Either change the route in `app/routes.py` from `"/links"` to `"/shorten"` (and update any internal references/tests), or revert the README back to `POST /links` to match the running code.

## Suggestions

- [minor] README.md:10 — The examples section also uses `/shorten`, so the same mismatch applies there. Ensure the example `curl` URL matches whatever route path is chosen.

## Looks good

- The change is intentionally scoped and easy to follow.
- Fail-loud auth default (503 when `LINKR_API_KEY` is unset) is a good design choice.

## Open questions

- Was there an intent to rename the route itself (in which case the code change is missing), or was the README updated prematurely?
