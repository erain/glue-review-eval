/** Top-level layout: sidebar + editor + preview, plus global keyboard shortcuts. */

import { useEffect } from 'react';
import NoteList from './components/NoteList';
import Editor from './components/Editor';
import Preview from './components/Preview';
import { useNotes } from './hooks/useNotes';
import './App.css';

export default function App() {
  const {
    sortedNotes,
    selectedId,
    selectedNote,
    createNote,
    deleteNote,
    updateBody,
    selectNote,
    flush,
  } = useNotes();

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const mod = e.metaKey || e.ctrlKey;
      if (!mod) return;
      const key = e.key.toLowerCase();
      if (key === 'n') {
        e.preventDefault();
        createNote();
      } else if (key === 's') {
        // Autosave already runs on a debounce; this just flushes the pending
        // write so the user sees the "saved" effect immediately.
        e.preventDefault();
        flush();
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [createNote, flush]);

  return (
    <div className="app">
      <NoteList
        notes={sortedNotes}
        selectedId={selectedId}
        onSelect={selectNote}
        onCreate={createNote}
        onDelete={deleteNote}
      />
      <main className="workspace">
        {selectedNote ? (
          <>
            <Editor
              value={selectedNote.body}
              onChange={(body) => updateBody(selectedNote.id, body)}
            />
            <Preview body={selectedNote.body} />
          </>
        ) : (
          <div className="workspace__empty">
            <p>No note selected.</p>
            <button type="button" onClick={createNote}>
              Create your first note
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
