/** Versioned localStorage wrapper for the notepad. */

import type { Note } from './types';

export const STORAGE_KEY = 'notepad.v1';

export interface StoredState {
  version: 1;
  notes: Note[];
  selectedId: string | null;
}

const EMPTY: StoredState = { version: 1, notes: [], selectedId: null };

type Storage = Pick<globalThis.Storage, 'getItem' | 'setItem' | 'removeItem'>;

function getStore(): Storage | null {
  try {
    if (typeof localStorage === 'undefined') return null;
    return localStorage;
  } catch {
    return null;
  }
}

/** Load persisted state. Returns a safe default on any error / missing data. */
export function loadState(store: Storage | null = getStore()): StoredState {
  if (!store) return { ...EMPTY };
  let raw: string | null;
  try {
    raw = store.getItem(STORAGE_KEY);
  } catch {
    return { ...EMPTY };
  }
  if (!raw) return { ...EMPTY };

  try {
    const parsed = JSON.parse(raw) as unknown;
    return normalize(parsed);
  } catch {
    return { ...EMPTY };
  }
}

/** Persist state. Errors (quota exceeded, disabled storage) are swallowed by design. */
export function saveState(state: StoredState, store: Storage | null = getStore()): void {
  if (!store) return;
  try {
    store.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Storage may be unavailable (private mode, quota, etc). The in-memory
    // copy remains authoritative — there's nothing actionable to do here.
  }
}

/** Wipe persisted state. Mostly for tests. */
export function clearState(store: Storage | null = getStore()): void {
  if (!store) return;
  try {
    store.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

function normalize(value: unknown): StoredState {
  if (!value || typeof value !== 'object') return { ...EMPTY };
  const obj = value as Record<string, unknown>;
  const notes = Array.isArray(obj.notes) ? obj.notes.map(coerceNote).filter(Boolean) as Note[] : [];
  const selectedId =
    typeof obj.selectedId === 'string' && notes.some((n) => n.id === obj.selectedId)
      ? obj.selectedId
      : notes[0]?.id ?? null;
  return { version: 1, notes, selectedId };
}

function coerceNote(value: unknown): Note | null {
  if (!value || typeof value !== 'object') return null;
  const n = value as Record<string, unknown>;
  if (typeof n.id !== 'string' || typeof n.body !== 'string') return null;
  const createdAt = typeof n.createdAt === 'number' ? n.createdAt : Date.now();
  const updatedAt = typeof n.updatedAt === 'number' ? n.updatedAt : createdAt;
  return { id: n.id, body: n.body, createdAt, updatedAt };
}
