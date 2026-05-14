```
## glue-review

DOMPurify removed from markdown pipeline — unsanitized HTML injected via `dangerouslySetInnerHTML`.

- **critical** — `src/utils/markdown.ts:19` — `DOMPurify.sanitize()` was the only XSS guard; removing it means malicious markdown (e.g., `<img onerror=...>`, `<a href="javascript:...">`) is rendered directly into the DOM via `dangerouslySetInnerHTML`.

`marked`'s built-in sanitisation is not enabled here (no `sanitize: true`) and, in modern `marked` versions, was removed entirely in favour of a dedicated sanitizer like DOMPurify.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/utils/markdown.ts** — Re-add the DOMPurify sanitisation step that was removed, or replace it with an equivalent XSS-sanitisation library.
   - Restore `import DOMPurify from 'dompurify';`
   - Restore the `DOMPurify.sanitize(html, { USE_PROFILES: { html: true }, FORBID_ATTR: ['style', 'onerror', 'onload'] })` call wrapping the `marked.parse()` result.
   - Update the JSDoc comments to accurately reflect that the output is sanitized before injection.
   Acceptance: `grep -n 'DOMPurify' src/utils/markdown.ts` returns a match, and `grep -n 'dangerouslySetInnerHTML' src/` shows the result is consumed in a way that requires sanitized input.
```
