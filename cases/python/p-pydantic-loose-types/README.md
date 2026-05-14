## p-pydantic-loose-types

**Category:** style - **Severity:** low - **Host:** python-linkr

The PR drops `AnyHttpUrl` from `LinkCreate.url` in `app/schemas.py` and
swaps in a plain `str`, with a comment claiming "more lenient parsing —
accepts file:// and custom schemes". It also rewrites the existing
`test_create_link_validates_url` (which used to post `"not-a-url"` and
assert 422) into a happy-path test that posts a `file://` URL and
expects 201.

The net effect is the only user-supplied field on POST /links has no
validation. Anything that's a string is accepted: `"not a url"`,
`"<script>"`, `""`. The PR simultaneously deletes the regression guard
that would have caught this.

The acceptance test `tests/test_link_validation.py::test_create_link_rejects_non_url_string`
posts `"not a url"` and expects 422 — fails on the planted code,
passes once a Pydantic URL type is restored. The reviewer should
identify the URL-type concept (HttpUrl / AnyHttpUrl / AnyUrl), point at
`app/schemas.py`, and call out that the existing validation test was
rewritten away.
