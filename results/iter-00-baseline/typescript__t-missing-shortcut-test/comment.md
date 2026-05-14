## Summary

Extracts global keyboard shortcut handling from `App.tsx` into a new `useShortcuts` hook, preserving identical behavior.

## Looks good

- Clean separation of concerns — keyboard shortcut logic is now self-contained and testable in its own hook.
- The `ShortcutHandlers` interface with JSDoc is a nice touch for discoverability.
- Behavior is preserved exactly: `Cmd/Ctrl+N` creates a note, `Cmd/Ctrl+S` flushes pending persistence.
- The `key.toLowerCase()` normalization and modifier check are unchanged from the original inline implementation.

## Open questions

- The `useEffect` dependency array references `onNewNote` and `onSave`, which are `createNote` and `flush` from `useNotes()`. If those aren't stable references (e.g., recreated on each render), the event listener will be torn down and re-registered every render. This was already the case before the extraction, so it's not a regression — just worth noting if the hook is reused elsewhere with unstable callbacks.
