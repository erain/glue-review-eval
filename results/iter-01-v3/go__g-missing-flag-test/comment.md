## glue-review

No concerns — LGTM.

The `--quote` flag and `plainQuoted` renderer are correct. The `init()` smoke test covers the new renderer at startup, and existing tests exercise plain/json rendering. The only note: `plainQuoted.Render` duplicates `plain.Render` nearly verbatim (only the tail-value quoting line differs). This is a reasonable trade-off for a small tool, but any future changes to `plain.Render`'s format will need to be replicated in `plainQuoted.Render` as well.
