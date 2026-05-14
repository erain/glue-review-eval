Let me check the `useNotes` hook to verify the return type matches what `NotesContext` expects.## Summary

Introduces a global `NotesContext` to eliminate prop-drilling: `useNotes()` now provides state through a React context provider, and `Editor`/`Preview` consume it directly instead of receiving props from `App`.

## Issues

None identified. The types, null-safety, and render-guard logic are all consistent.

## Suggestions

- [minor] src/contexts/NotesContext.tsx:22 — The context value object is re-created on every render (`useNotes()` returns a new object literal each call), which will cause all consumers to re-render even when underlying values haven't changed. Consider memoizing stable slices or the entire value with `useMemo` to avoid unnecessary consumer updates. Fix: In `NotesProvider`, wrap the api object in `useMemo`: `const api = useMemo(() => useNotes(), [])` — though note that `useNotes` itself uses `useCallback`/`useMemo` internally, so individual return values (like `sortedNotes`, `selectedNote`) are already referentially stable between state changes; the outer object wrapper is the only unstable reference.

- [minor] src/components/Editor.tsx:18 — The `disabled` prop from the original `EditorProps` interface has been removed and replaced with an internally computed `!selectedNote`. This is fine functionally (the old caller never passed `disabled`), but if any future consumer needs to force-disable the editor independently of selection state, they would need to thread a prop back in. Worth a brief note in the PR description.

## Looks good

- Context type (`UseNotesApi | null`) aligns exactly with `useNotes()` return type — no type drift.
- `useNotesContext()` correctly throws if used outside a `<NotesProvider>`, failing fast rather than silently returning `null`.
- `Editor` and `Preview` safely guard against `selectedNote` being null with optional chaining and fallback values.
- `NoteList` is intentionally kept as a prop-based consumer for test migration — the inline comment explains this clearly.
- `flush` (Cmd/Ctrl+S) continues to be destructured in `App` and works through context.
- No behavioral change from the user's perspective — same rendering logic, same guards.

## Open questions

None — the diff, commit message, and supporting types all tell a coherent story.
