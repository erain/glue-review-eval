/** Live-rendered markdown preview, sanitized via DOMPurify. */

import { useMemo } from 'react';
import { renderMarkdown } from '../utils/markdown';

export interface PreviewProps {
  body: string;
}

export default function Preview({ body }: PreviewProps) {
  const html = useMemo(() => renderMarkdown(body), [body]);
  return (
    <div
      className="preview"
      aria-label="Note preview"
      // Safe: DOMPurify-sanitized output. See utils/markdown.ts.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
