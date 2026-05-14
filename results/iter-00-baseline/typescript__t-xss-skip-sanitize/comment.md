The diff is small — one file, one concern. Let me check if the Preview component mentioned in the comment does any compensating sanitization.## Summary
This branch removes DOMPurify sanitization from the `renderMarkdown` pipeline, which is called via `dangerouslySetInnerHTML` in the Preview component.

## Issues
- **[critical] src/utils/markdown.ts:14** — DOMPurify sanitization has been removed from the markdown-to-HTML pipeline, but the output is still injected via `dangerouslySetInnerHTML` in `Preview.tsx`. This is an XSS regression: any malicious payload in markdown (e.g., `<img onerror="...">`, `<a href="javascript:...">`, inline `<style>`) will now execute/render unsanitized. Fix: Restore the DOMPurify import and `sanitize()` call in `renderMarkdown()` in `src/utils/markdown.ts`, or alternatively add a DOMPurify pass in the Preview component before assigning to `dangerouslySetInnerHTML`.

- **[minor] src/components/Preview.tsx:8** — The comment `// Safe: DOMPurify-sanitized output. See utils/markdown.ts.` is now stale and misleading since DOMPurify has been removed from the referenced file. Fix: Update or remove the comment in Preview.tsx to reflect the actual sanitization state.

## Looks good
Nothing in the diff is well-done — the core change introduces a security regression.

## Open questions
- Was this an intentional performance optimization that accepted the XSS risk, or an accidental drop? If intentional, was a Content Security Policy (CSP) added as a compensating control?
- Are there other consumers of `renderMarkdown` besides Preview that might also be affected?
