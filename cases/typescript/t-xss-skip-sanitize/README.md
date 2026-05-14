# t-xss-skip-sanitize

**Category:** security · **Severity:** critical · **Host:** ts-notepad

`src/utils/markdown.ts` is the choke point between user-supplied
markdown and the `dangerouslySetInnerHTML` injection in `Preview.tsx`.
The PR removes the `DOMPurify.sanitize(...)` pass, justifying it as a
performance simplification.

Three host tests fall over immediately (script tags, inline event
handlers, `javascript:` URLs), so the reviewer should latch onto the
sanitisation contract and the fix-block must direct the coding agent to
restore the DOMPurify call with the same `FORBID_ATTR` list. Notes are
persisted to localStorage so this is a stored-XSS surface, not a
transient render concern.
