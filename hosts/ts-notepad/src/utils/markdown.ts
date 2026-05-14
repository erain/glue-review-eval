/** Markdown -> sanitized HTML pipeline. */

import { marked } from 'marked';
import DOMPurify from 'dompurify';

marked.setOptions({
  gfm: true,
  breaks: false,
});

/**
 * Render markdown to safe HTML.
 *
 * marked is configured synchronously (no async extensions), so we cast its return
 * value to string. The output is then run through DOMPurify before being injected
 * via `dangerouslySetInnerHTML`.
 */
export function renderMarkdown(body: string): string {
  const html = marked.parse(body ?? '', { async: false }) as string;
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    // Tighten the default config: no inline event handlers, no `javascript:` URLs.
    FORBID_ATTR: ['style', 'onerror', 'onload'],
  });
}
