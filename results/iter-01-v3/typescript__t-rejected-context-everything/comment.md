## glue-review

No concerns — LGTM.

The context extraction is clean: `NotesProvider` wraps `useNotes()`, `useNotesContext()` throws appropriately when used outside the provider, and `Editor`/`Preview` correctly read from context with null guards. The App.tsx comment explicitly acknowledges that test migration is deferred, which is fine as a staged refactor.

One thing to watch: `EditorProps` and `PreviewProps` exports are removed in this diff — any files that import those types (outside this diff) will get a TypeScript error until their consumers are updated.
