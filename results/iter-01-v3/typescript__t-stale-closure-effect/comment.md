Let me read the full hook file to confirm the stale closure issue.```markdown
## glue-review

Stale closure in `useEffect` blur handler — `snapshot` captures the initial `state` value and never updates, so the blur handler always persists the state from mount time, not the latest edits.

- **high** — `src/hooks/useNotes.ts:75` — `const snapshot = state` inside a `useEffect(() => { ... }, [])` captures `state` once at mount; the `onBlur` callback will always save that stale snapshot instead of the current state.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/hooks/useNotes.ts:72-82** — The `useEffect` with `[]` captures `state` as a stale closure. The blur handler will always persist the initial mount-time snapshot, not the latest state.
   - Import `useRef` from React.
   - Add a `const stateRef = useRef(state);` right before the effect.
   - Update `stateRef.current = state;` at the top of the effect body (so the ref always holds the latest value).
   - Change `saveState(snapshot)` inside `onBlur` to `saveState(stateRef.current)`.
   - Keep the `[]` dependency array so the listener is only registered once.
   Acceptance: `npx vitest run src/__tests__/stale-closure.test.tsx` passes — the test verifies that the *second* edit survives a blur cycle, which the stale closure would lose.
```
