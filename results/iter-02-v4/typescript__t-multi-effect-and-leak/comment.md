## glue-review

Timer leak and stale closure in the new `Editor` component's `useEffect`.

- **high** — `src/components/Editor.tsx:36` — `useEffect` sets a `setTimeout` on every `value` change but never clears it in the cleanup function; rapid note switches accumulate one timer per change, which will fail the new test at `vi.getTimerCount() <= 1`.
- **medium** — `src/components/Editor.tsx:34` — `useEffect` depends on `[value]` but not `noteId`; switching to a different note that happens to share the same body text leaves a stale closure where the pending callback still references the old `noteId`.
- **low** — `src/__tests__/editor-leak.test.tsx` covers timer leaks but there is no test for the `disabled` prop interaction (e.g., that a disabled editor never shows the unsaved pip).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/components/Editor.tsx line ~35** — `useEffect` does not clear its timeout on cleanup, causing one leaked `setTimeout` per keystroke / note switch.
   - Store the return value of `setTimeout` and return a cleanup function that calls `clearTimeout(timer)`.
   - Also add `noteId` to the dependency array so the effect re-arms (and clears the old timer) when the active note changes.
   - The fixed effect should look roughly like:
     ```tsx
     useEffect(() => {
       if (!value) return;
       const timer = setTimeout(() => {
         setUnsavedFor((prev) => (prev === noteId ? null : prev));
       }, UNSAVED_FLASH_MS);
       return () => clearTimeout(timer);
     }, [value, noteId]);
     ```
   Acceptance: `npx vitest run src/__tests__/editor-leak.test.tsx` passes (timer count ≤ 1 after 5 rapid rerenders).

2. **tests (optional)** — Add a test exercising that a `disabled` Editor never sets the unsaved pip.
   Acceptance: A new test or case that mounts `<Editor disabled value="x" />`, fires onChange, and asserts that no `.editor__unsaved` element appears.
```
