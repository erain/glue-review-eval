Let me inspect the current state of the changed files more closely.Let me check if the debounce hook is still referenced anywhere else.## glue-review

New test `persistence-debounce.test.ts` validates the old debounce behavior that was explicitly removed — it will fail with the new code (expects ≤ 2 localStorage writes for 10 edits, but the new `useEffect` writes on every state change, producing 10).

- **high** — `src/__tests__/persistence-debounce.test.ts:32` — Assertion expects `≤ 2` `setItem` calls after 10 rapid edits, but the removed debounce means every `updateBody` now triggers an immediate `saveState`, producing ~10 writes. This test will fail.
- **medium** — `src/hooks/useNotes.ts:28` — JSDoc on `flush` says "Force-flush any pending persistence" but there is nothing pending anymore since `useEffect` writes synchronously on every state change.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/__tests__/persistence-debounce.test.ts:32** — The test validates debounce coalescing behavior that was deliberately removed. Rewrite or remove this test.
   - Option A (recommended): Delete the file entirely since the debounce feature no longer exists and there is nothing to assert.
   - Option B: Rewrite the test to verify that every state change triggers a `setItem` (e.g., assert `spy.mock.calls.length === 11` — 1 from createNote + 10 from updateBody).
   Acceptance: Either the file is removed, or the assertion matches the new non-debounced behavior (all 11 writes fire).

2. **src/hooks/useNotes.ts:28** — Update the JSDoc for `flush` to reflect that it is now a synchronous re-save rather than a debounce flush.
   - Change the docstring from "Force-flush any pending persistence (Cmd/Ctrl+S)" to "Force-write current state to localStorage (Cmd/Ctrl+S)".
   Acceptance: The comment no longer references "pending" or "flush" in the debounce sense.
```
