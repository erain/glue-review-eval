Let me read the full Editor component to understand the current code in detail.## glue-review

Timer leak in `useEffect`: previous `setTimeout` is never cleared when `value` changes, and `noteId` is missing from the dependency array causing stale closures on rapid note switches.

- **high** — `src/components/Editor.tsx:27` — `useEffect` creates a `setTimeout` on every `value` change but never returns a cleanup function to clear the prior timer, so timers accumulate (the new test at line 29 would fail: `vi.getTimerCount()` returns 5, not `<=1`).
- **medium** — `src/components/Editor.tsx:27` — `noteId` is used inside the timeout callback but is not in the effect's dependency array (`[value]`); switching to a different note with the same body text leaves a stale `noteId` closure, so the wrong indicator gets cleared or the new note's pip is never auto-cleared.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/components/Editor.tsx:24–29** — `useEffect` for the auto-clear timer leaks because it never cleans up the previous timeout, and `noteId` is missing from the dependency array.
   - Save the timeout handle: `const timer = setTimeout(() => { ... }, UNSAVED_FLASH_MS);`
   - Return a cleanup that clears it: `return () => clearTimeout(timer);`
   - Add `noteId` to the dependency array so the effect re-runs when the active note changes: change `[value]` to `[value, noteId]`.
   Acceptance: `npx vitest run src/__tests__/editor-leak.test.tsx` passes (timer count `<= 1`).
```
