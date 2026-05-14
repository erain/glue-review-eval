## glue-review

New debounce test contradicts the PR's intentional removal of debouncing — `persistence-debounce.test.ts` will fail.

- **high** — `src/__tests__/persistence-debounce.test.ts:30` — Expects at most 2 localStorage writes after 10 rapid edits, but the hook now calls `saveState` synchronously on every state change, so 10 writes will occur.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/__tests__/persistence-debounce.test.ts** — The debounce behavior tested here was intentionally removed in `useNotes.ts`. This test will fail (expects ≤2 writes but gets 10+).
   - Either delete the file entirely since debounce no longer exists, or rewrite it to verify that writes happen immediately on each state change (e.g., `expect(spy.mock.calls.length).toBe(10)` for 10 edits).
   Acceptance: `npx vitest run src/__tests__/persistence-debounce.test.ts` passes.
```
