import { describe, expect, it } from 'vitest';
import { renderMarkdown } from '../utils/markdown';

describe('renderMarkdown', () => {
  it('renders a heading', () => {
    const html = renderMarkdown('# Hello');
    expect(html).toContain('<h1');
    expect(html).toContain('Hello');
  });

  it('renders an unordered list', () => {
    const html = renderMarkdown('- a\n- b');
    expect(html).toContain('<ul>');
    expect(html).toMatch(/<li>\s*a\s*<\/li>/);
  });

  it('renders fenced code blocks', () => {
    const html = renderMarkdown('```\nconst x = 1;\n```');
    expect(html).toContain('<pre>');
    expect(html).toContain('<code');
    expect(html).toContain('const x = 1;');
  });

  it('strips script tags', () => {
    const html = renderMarkdown('hi <script>alert(1)</script>');
    expect(html).not.toContain('<script');
    expect(html).not.toContain('alert(1)');
  });

  it('strips inline event handlers', () => {
    const html = renderMarkdown('<img src="x" onerror="alert(1)">');
    expect(html).not.toMatch(/onerror=/i);
  });

  it('drops javascript: hrefs', () => {
    const html = renderMarkdown('[click](javascript:alert(1))');
    expect(html.toLowerCase()).not.toContain('javascript:');
  });

  it('returns an empty string for empty input', () => {
    expect(renderMarkdown('').trim()).toBe('');
  });
});
