Let me read the full source file to understand the state management.The diff adds a `useEffect` to save state on window blur, but it has a **stale closure** — the `onBlur` handler captures `state` once on mount and never sees updates. This is precisely the bug the new test is meant to catch.

```diff
  useEffect(() => {
-    const snapshot = state;
    function onBlur() {
-      saveState(snapshot);
+      saveState(stateRef.current);
    }
```

## glue-review

**Stale closure in on-blur persistence handler**

- **critical** — `src/hooks/useNotes.ts:78` — The `useEffect(() => { const snapshot = state; ... onBlur() { saveState(snapshot) } }, [])` captures `state` once at mount; every subsequent blur saves the initial (empty) snapshot instead of the current state.
- **medium** — `src/__tests__/stale-closure.test.tsx:17-38` — The regression test exists but will not reliably pass because the blur handler saves a stale closure value; it only passes incidentally if the debounced `useDebouncedEffect` re-saves after the blur.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/hooks/useNotes.ts** (lines 77-87) — The blur-handler closure captures `state` on mount and never sees updates.
   - Add `useRef` to the React import: change `import { useCallback, useEffect, useMemo, useState } from 'react'` to `import { useCallback, useEffect, useMemo, useRef, useState } from 'react'`.
   - Add a ref that tracks the latest state: insert `const stateRef = useRef(state); stateRef.current = state;` just before the `useEffect` block.
   - In the `onBlur` handler, replace `saveState(snapshot)` with `saveState(stateRef.current)` and remove the `const snapshot = state` line.
   Acceptance: `npx vitest run src/__tests__/stale-closure.test.tsx` passes (1 passing).
```
