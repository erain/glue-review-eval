import { describe, expect, it } from 'vitest';
import { STORAGE_KEY, clearState, loadState, saveState, type StoredState } from '../storage';

function makeStore(initial: Record<string, string> = {}): Storage {
  const data = new Map(Object.entries(initial));
  return {
    getItem: (k) => (data.has(k) ? (data.get(k) as string) : null),
    setItem: (k, v) => {
      data.set(k, v);
    },
    removeItem: (k) => {
      data.delete(k);
    },
    clear: () => data.clear(),
    key: (i) => Array.from(data.keys())[i] ?? null,
    get length() {
      return data.size;
    },
  } as Storage;
}

describe('storage', () => {
  it('returns empty state when nothing is stored', () => {
    const store = makeStore();
    expect(loadState(store)).toEqual({ version: 1, notes: [], selectedId: null });
  });

  it('round-trips a saved state', () => {
    const store = makeStore();
    const state: StoredState = {
      version: 1,
      notes: [
        { id: 'a', body: '# hi', createdAt: 1, updatedAt: 2 },
        { id: 'b', body: 'plain', createdAt: 3, updatedAt: 4 },
      ],
      selectedId: 'b',
    };
    saveState(state, store);
    expect(loadState(store)).toEqual(state);
  });

  it('recovers from corrupt JSON', () => {
    const store = makeStore({ [STORAGE_KEY]: '{not-json' });
    expect(loadState(store)).toEqual({ version: 1, notes: [], selectedId: null });
  });

  it('drops notes with missing required fields', () => {
    const store = makeStore({
      [STORAGE_KEY]: JSON.stringify({
        notes: [
          { id: 'ok', body: 'hello', createdAt: 1, updatedAt: 1 },
          { id: 'bad' }, // missing body
          { body: 'no id' },
          null,
        ],
        selectedId: 'ok',
      }),
    });
    const state = loadState(store);
    expect(state.notes).toHaveLength(1);
    expect(state.notes[0].id).toBe('ok');
    expect(state.selectedId).toBe('ok');
  });

  it('resets selectedId if the stored id is gone', () => {
    const store = makeStore({
      [STORAGE_KEY]: JSON.stringify({
        notes: [{ id: 'a', body: 'x', createdAt: 1, updatedAt: 1 }],
        selectedId: 'does-not-exist',
      }),
    });
    expect(loadState(store).selectedId).toBe('a');
  });

  it('clearState removes the key', () => {
    const store = makeStore();
    saveState({ version: 1, notes: [], selectedId: null }, store);
    clearState(store);
    expect(store.getItem(STORAGE_KEY)).toBeNull();
  });

  it('tolerates a storage that throws', () => {
    const broken: Storage = {
      getItem: () => {
        throw new Error('nope');
      },
      setItem: () => {
        throw new Error('nope');
      },
      removeItem: () => {
        throw new Error('nope');
      },
      clear: () => {},
      key: () => null,
      length: 0,
    } as Storage;
    expect(() => loadState(broken)).not.toThrow();
    expect(() => saveState({ version: 1, notes: [], selectedId: null }, broken)).not.toThrow();
    expect(() => clearState(broken)).not.toThrow();
  });
});
