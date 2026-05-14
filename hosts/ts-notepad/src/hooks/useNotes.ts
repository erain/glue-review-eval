/** Note CRUD + selection state with debounced localStorage persistence. */

import { useCallback, useMemo, useState } from 'react';
import { loadState, saveState, type StoredState } from '../storage';
import { newNote, titleOf, type Note } from '../types';
import { useDebouncedEffect } from './useDebounce';

const PERSIST_DELAY_MS = 300;

export interface UseNotesApi {
  notes: Note[];
  /** Notes sorted by `updatedAt` descending — what the sidebar should render. */
  sortedNotes: Array<Note & { title: string }>;
  selectedId: string | null;
  selectedNote: Note | null;
  createNote: () => Note;
  deleteNote: (id: string) => void;
  updateBody: (id: string, body: string) => void;
  selectNote: (id: string) => void;
  /** Force-flush any pending persistence (Cmd/Ctrl+S). */
  flush: () => void;
}

/** Stateful hook backing the whole app. Single source of truth for notes. */
export function useNotes(): UseNotesApi {
  const [state, setState] = useState<StoredState>(() => loadState());

  const flush = useDebouncedEffect(state, PERSIST_DELAY_MS, saveState);

  const createNote = useCallback((): Note => {
    const note = newNote();
    setState((prev) => ({
      version: 1,
      notes: [note, ...prev.notes],
      selectedId: note.id,
    }));
    return note;
  }, []);

  const deleteNote = useCallback((id: string) => {
    setState((prev) => {
      const notes = prev.notes.filter((n) => n.id !== id);
      const selectedId =
        prev.selectedId === id
          ? // After deleting the selected note, fall back to the most recently
            // updated remaining note (sidebar order) so the editor stays useful.
            [...notes].sort((a, b) => b.updatedAt - a.updatedAt)[0]?.id ?? null
          : prev.selectedId;
      return { version: 1, notes, selectedId };
    });
  }, []);

  const updateBody = useCallback((id: string, body: string) => {
    setState((prev) => {
      const now = Date.now();
      const notes = prev.notes.map((n) =>
        n.id === id ? { ...n, body, updatedAt: now } : n,
      );
      return { ...prev, notes };
    });
  }, []);

  const selectNote = useCallback((id: string) => {
    setState((prev) =>
      prev.notes.some((n) => n.id === id) ? { ...prev, selectedId: id } : prev,
    );
  }, []);

  const sortedNotes = useMemo(
    () =>
      [...state.notes]
        .sort((a, b) => b.updatedAt - a.updatedAt)
        .map((n) => ({ ...n, title: titleOf(n.body) })),
    [state.notes],
  );

  const selectedNote = useMemo(
    () => state.notes.find((n) => n.id === state.selectedId) ?? null,
    [state.notes, state.selectedId],
  );

  return {
    notes: state.notes,
    sortedNotes,
    selectedId: state.selectedId,
    selectedNote,
    createNote,
    deleteNote,
    updateBody,
    selectNote,
    flush,
  };
}
