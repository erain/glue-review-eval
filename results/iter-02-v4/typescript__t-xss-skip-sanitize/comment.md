```
## glue-review

**Pushback on approach** — removing DOMPurify from the markdown render pipeline introduces an XSS vulnerability.

The `renderMarkdown` output is injected via `dangerouslySetInnerHTML` (noted in the updated docstring). Without DOMPurify, any user-supplied markdown that produces `<script>`, `onerror=`, `onload=`, `javascript:` URLs, or other executable HTML will execute in the browser. The previous code explicitly forbid these vectors via `FORBID_ATTR` and the full HTML profile — dropping that pass entirely removes the only defense between untrusted markdown input and DOM execution.

---

### Fix instructions — paste into your coding agent

```markdown
Do NOT apply the current diff. Instead:

1. Restore the DOMPurify import and sanitization call in `src/utils/markdown.ts` — specifically the `DOMPurify.sanitize(html, { USE_PROFILES: { html: true }, FORBID_ATTR: ['style', 'onerror', 'onload'] })` call inside `renderMarkdown`.
2. If the goal is to reduce bundle size or simplify the pipeline, evaluate switching to a DOMPurify lightweight build or a sandboxed iframe approach — but do not remove client-side sanitization of `dangerouslySetInnerHTML` content entirely.
   Acceptance: `grep -n "DOMPurify" src/utils/markdown.ts` returns a match, and the renderMarkdown function passes output through `DOMPurify.sanitize()` before returning.
```
```
