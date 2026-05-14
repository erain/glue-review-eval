# notepad

A small markdown notepad. React + TypeScript + Vite, with notes persisted to
`localStorage`. Two dependencies do the heavy lifting: `marked` for parsing
and `dompurify` for sanitizing the rendered HTML.

## Features

- Sidebar list of notes, sorted by `updatedAt` descending.
- Split editor / live preview pane.
- Note titles are derived from the first H1 (or first non-empty line as a
  fallback) — no separate title field to keep in sync.
- Debounced autosave to `localStorage` (~300 ms). `Cmd/Ctrl+S` force-flushes
  the pending write. `Cmd/Ctrl+N` creates a new note.
- The preview pipeline runs `marked` then `DOMPurify`, so pasting raw HTML
  with `<script>` or `onerror=` handlers is safe.

## Develop

```sh
npm install
npm run dev       # http://localhost:5173
npm run build     # tsc -b && vite build
npm test          # vitest run
```

## Storage

State lives under a single localStorage key, `notepad.v1`. The shape is
`{ version: 1, notes: Note[], selectedId: string | null }`. Loader code is
defensive: corrupt JSON, missing fields, or a dangling `selectedId` all fall
back to a sane default rather than crashing the app.

## Layout

```
src/
  App.tsx, main.tsx          UI shell + entry
  components/                NoteList, Editor, Preview
  hooks/                     useNotes, useDebounce
  storage.ts                 localStorage wrapper
  types.ts                   Note interface + titleOf()
  utils/markdown.ts          marked + DOMPurify pipeline
  __tests__/                 vitest suites
```
