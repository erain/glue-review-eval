/** Note data model and derivation helpers. */

export interface Note {
  id: string;
  body: string;
  createdAt: number;
  updatedAt: number;
}

/**
 * Derive a display title from a note body.
 *
 * Rules:
 *   1. First leading `# Heading` line (ATX H1) wins.
 *   2. Otherwise, first non-empty line, with any leading markdown punctuation trimmed.
 *   3. Otherwise, the literal string "Untitled".
 *
 * The title is also length-capped so long first lines do not blow up the sidebar.
 */
export function titleOf(body: string): string {
  const TITLE_MAX = 80;
  const lines = body.split(/\r?\n/);

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    const h1 = line.match(/^#\s+(.+?)\s*#*\s*$/);
    if (h1) return clamp(h1[1], TITLE_MAX);
    // Not an H1 — fall through to the "first non-empty line" rule.
    const stripped = line.replace(/^[#>\-*+`~\s]+/, '').trim();
    return clamp(stripped || line, TITLE_MAX);
  }

  return 'Untitled';
}

function clamp(s: string, max: number): string {
  return s.length > max ? `${s.slice(0, max - 1).trimEnd()}…` : s;
}

/** Create a fresh empty note with sensible defaults. */
export function newNote(now: number = Date.now()): Note {
  return {
    id: uuid(),
    body: '',
    createdAt: now,
    updatedAt: now,
  };
}

/** RFC4122-ish v4 UUID. Uses crypto.randomUUID when available, else a Math.random fallback. */
export function uuid(): string {
  const g = globalThis as { crypto?: { randomUUID?: () => string } };
  if (g.crypto?.randomUUID) return g.crypto.randomUUID();
  // Fallback for older runtimes / jsdom configs without randomUUID.
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
