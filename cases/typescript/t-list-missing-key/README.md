# t-list-missing-key

**Category:** style - **Severity:** medium - **Host:** ts-notepad

`NoteList.tsx` maps `notes` to `<li>` elements. The PR drops the
`key={note.id}` prop on the assumption that iteration order is
stable. It is not — `sortedNotes` reorders by `updatedAt` whenever a
note is edited, so positional reconciliation will move component
state to the wrong row and React emits a missing-key warning every
render.

`src/__tests__/NoteList.keys.test.tsx` spies on `console.error` and
fails on any log matching React's missing-key message. The fix is to
put `key={note.id}` back on the `<li>` and drop the misleading
justification comment.
