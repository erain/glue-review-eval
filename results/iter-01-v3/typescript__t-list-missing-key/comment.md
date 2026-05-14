```
## glue-review

**Pushback on approach** — dropping `key` from list items trades a React safety net for a fragile assumption about sort stability.

The `key` prop exists so React can correctly track identity across re-renders when items are added, removed, or reordered. The comment claims "no need for an explicit key when iteration is stable," but that reasoning has holes:

- Even with a stable sort, a note update that changes `updatedAt` can shift its position in the list. Without keys, React will reconcile by index, potentially attaching stale component state (e.g., collapsed/expanded UI state on a note card, focus state, animation state) to the wrong item.
- If a note is deleted, every item after it in the list gets re-associated with the wrong DOM node.
- The upstream sort guarantee is an implementation detail of the parent/module, not an invariant this component should rely on. If the sort logic ever changes, this silently breaks.

The new test only verifies the absence of React's dev-mode warning — it doesn't test for the actual bugs that missing keys can introduce.

---

### Fix instructions — paste into your coding agent

```markdown
Do NOT keep the current diff as-is. Instead:

1. **`src/components/NoteList.tsx`** line 41 — Restore `key={note.id}` on the `<li>` element so React can correctly reconcile list items by identity.
   - Revert `return (<li>)` back to `return (<li key={note.id}>)`.
   - Remove the inline comment about sorted/iteration-stable since it no longer applies.

2. **`src/__tests__/NoteList.keys.test.tsx`** — Either delete this test entirely (it was only added to justify removing the key), or convert it into a test that verifies keys ARE present and no React warning is emitted (which is the default behavior when keys are supplied).
   - If converting: update the test to assert that `<li>` elements carry `key` attributes or simply assert the component renders without errors.
   - If deleting: remove the file.

   Acceptance: `vitest run` passes. Confirm `<li>` elements in `<NoteList>` have `key={note.id}` by grepping: `grep -n 'key=' src/components/NoteList.tsx` shows the key on the `<li>`.
```
