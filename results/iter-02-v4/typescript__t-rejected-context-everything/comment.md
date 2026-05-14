Let me check for any test files or other references that might be affected.Let me check the existing hook and any test files that might be affected.Let me check for any other consumers of the removed interfaces and the overall project structure.## glue-review

Context refactor from prop-drilling to `NotesContext` is clean but has a few concerns worth addressing.

- **medium** — `EditorProps` and `PreviewProps` interfaces are deleted; any existing tests or consumers that import/render `<Editor value={...} onChange={...} />` or `<Preview body={...} />` will break at compile time and need updating to the new zero-prop signatures.
- **medium** — `Editor` and `Preview` now require an ancestor `<NotesProvider>` to render. Any standalone tests (e.g., in Storybook or isolated test files) will throw `"useNotesContext must be used inside a <NotesProvider>"` unless wrapped.
- **low** — `onChange` in `Editor` creates a new closure on every render. Not a bug, but worth wrapping in `useCallback` once `selectedNote?.id` is needed in the dependency array to keep the reference stable across renders.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/components/Editor.tsx** — `onChange` arrow function is recreated every render.
   - Wrap the handler in `useCallback` with `[selectedNote?.id, updateBody]` as dependencies, or at minimum extract it so the reference doesn't force re-mount of the controlled textarea.
   - Acceptance: `selectedNote` is non-null when the textarea is enabled; changing notes and typing produces a single `updateBody` call with the correct note id (manual flow test or existing integration test).

2. **src/components/Editor.tsx, src/components/Preview.tsx** — components can no longer be rendered outside a `<NotesProvider>`.
   - Add a test file (e.g., `tests/EditorWithContext.test.tsx`) that wraps `<Editor />` in `<NotesProvider>` and asserts it renders without throwing.
   - Add a similar test for `<Preview />`.
   - Acceptance: `npx jest --testPathPattern="EditorWithContext|PreviewWithContext" --no-coverage` passes.

3. **Any existing test files referencing `EditorProps` or `PreviewProps`** — search the repo for imports of these deleted interfaces.
   - If found, remove the import and update the test to use the new zero-prop component signature.
   - Acceptance: TypeScript compilation (`npx tsc --noEmit`) succeeds with no undefined-type errors.
```
