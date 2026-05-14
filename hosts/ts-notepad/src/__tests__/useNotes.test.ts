import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useNotes } from '../hooks/useNotes';
import { STORAGE_KEY, loadState } from '../storage';
import { titleOf } from '../types';

beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe('titleOf', () => {
  it('returns H1 when present', () => {
    expect(titleOf('# My note\n\nbody')).toBe('My note');
  });

  it('falls back to the first non-empty line', () => {
    expect(titleOf('\n\nfirst line\nsecond')).toBe('first line');
  });

  it('strips markdown punctuation from the fallback', () => {
    expect(titleOf('> a quote')).toBe('a quote');
    expect(titleOf('- bullet')).toBe('bullet');
  });

  it('returns Untitled for empty body', () => {
    expect(titleOf('')).toBe('Untitled');
    expect(titleOf('   \n   ')).toBe('Untitled');
  });

  it('clamps very long titles', () => {
    const long = 'x'.repeat(200);
    const out = titleOf(long);
    expect(out.length).toBeLessThanOrEqual(80);
    expect(out.endsWith('…')).toBe(true);
  });
});

describe('useNotes', () => {
  it('starts empty', () => {
    const { result } = renderHook(() => useNotes());
    expect(result.current.notes).toEqual([]);
    expect(result.current.selectedId).toBeNull();
    expect(result.current.selectedNote).toBeNull();
  });

  it('creates and selects a note', () => {
    const { result } = renderHook(() => useNotes());
    act(() => {
      result.current.createNote();
    });
    expect(result.current.notes).toHaveLength(1);
    expect(result.current.selectedId).toBe(result.current.notes[0].id);
    expect(result.current.selectedNote?.id).toBe(result.current.notes[0].id);
  });

  it('updates body and bumps updatedAt', () => {
    const { result } = renderHook(() => useNotes());
    let id = '';
    act(() => {
      id = result.current.createNote().id;
    });
    const before = result.current.notes[0].updatedAt;
    vi.advanceTimersByTime(10);
    act(() => {
      result.current.updateBody(id, '# Hello');
    });
    expect(result.current.selectedNote?.body).toBe('# Hello');
    expect(result.current.notes[0].updatedAt).toBeGreaterThanOrEqual(before);
    expect(result.current.sortedNotes[0].title).toBe('Hello');
  });

  it('sorts by updatedAt desc', () => {
    const { result } = renderHook(() => useNotes());
    const ids: string[] = [];
    act(() => {
      ids.push(result.current.createNote().id);
    });
    vi.advanceTimersByTime(5);
    act(() => {
      ids.push(result.current.createNote().id);
    });
    vi.advanceTimersByTime(5);
    // Touch the first one — it should jump to the top.
    act(() => {
      result.current.updateBody(ids[0], 'edit');
    });
    expect(result.current.sortedNotes[0].id).toBe(ids[0]);
    expect(result.current.sortedNotes[1].id).toBe(ids[1]);
  });

  it('deletes a note and selects the next-most-recent', () => {
    const { result } = renderHook(() => useNotes());
    const ids: string[] = [];
    act(() => {
      ids.push(result.current.createNote().id);
    });
    vi.advanceTimersByTime(5);
    act(() => {
      ids.push(result.current.createNote().id);
    });
    // Newest is ids[1] and is the current selection.
    expect(result.current.selectedId).toBe(ids[1]);
    act(() => {
      result.current.deleteNote(ids[1]);
    });
    expect(result.current.notes).toHaveLength(1);
    expect(result.current.selectedId).toBe(ids[0]);
  });

  it('selectNote ignores unknown ids', () => {
    const { result } = renderHook(() => useNotes());
    act(() => {
      result.current.createNote();
    });
    const before = result.current.selectedId;
    act(() => {
      result.current.selectNote('nope');
    });
    expect(result.current.selectedId).toBe(before);
  });

  it('persists to localStorage after the debounce window', () => {
    const { result } = renderHook(() => useNotes());
    act(() => {
      result.current.createNote();
    });
    // Right after creation — nothing yet.
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    act(() => {
      vi.advanceTimersByTime(350);
    });
    const persisted = loadState(localStorage);
    expect(persisted.notes).toHaveLength(1);
  });

  it('flush writes immediately without waiting for the debounce', () => {
    const { result } = renderHook(() => useNotes());
    act(() => {
      result.current.createNote();
    });
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    act(() => {
      result.current.flush();
    });
    expect(localStorage.getItem(STORAGE_KEY)).not.toBeNull();
  });
});
