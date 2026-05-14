/** Sidebar list of notes, sorted by updatedAt desc. */

import type { Note } from '../types';

export interface NoteListProps {
  notes: Array<Note & { title: string }>;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
}

export default function NoteList({
  notes,
  selectedId,
  onSelect,
  onCreate,
  onDelete,
}: NoteListProps) {
  return (
    <aside className="note-list" aria-label="Notes">
      <div className="note-list__toolbar">
        <button type="button" onClick={onCreate} aria-label="New note">
          New
        </button>
        <button
          type="button"
          onClick={() => selectedId && onDelete(selectedId)}
          disabled={!selectedId}
          aria-label="Delete selected note"
        >
          Delete
        </button>
      </div>
      {notes.length === 0 ? (
        <p className="note-list__empty">No notes yet. Hit "New" to start.</p>
      ) : (
        <ul className="note-list__items" role="listbox" aria-label="Note titles">
          {notes.map((note) => {
            const selected = note.id === selectedId;
            return (
              <li key={note.id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected}
                  className={
                    selected ? 'note-list__item note-list__item--selected' : 'note-list__item'
                  }
                  onClick={() => onSelect(note.id)}
                >
                  <span className="note-list__title">{note.title}</span>
                  <time className="note-list__time" dateTime={new Date(note.updatedAt).toISOString()}>
                    {formatTime(note.updatedAt)}
                  </time>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </aside>
  );
}

function formatTime(ms: number): string {
  const d = new Date(ms);
  const today = new Date();
  const sameDay =
    d.getFullYear() === today.getFullYear() &&
    d.getMonth() === today.getMonth() &&
    d.getDate() === today.getDate();
  if (sameDay) {
    return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}
