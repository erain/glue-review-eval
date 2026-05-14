Let me read the current state of the Editor component to confirm the details.## Summary

This branch adds an "unsaved" flash indicator to the `Editor` component: when a user types, a purple "unsaved" pip appears next to the note title and auto-clears after 1.5 seconds of inactivity. A new test verifies that timers don't leak when switching notes rapidly.

## Issues

- [critical] `src/components/Editor.tsx:23` — The `useEffect` that arms the auto-clear timeout does not return a cleanup function, so `setTimeout` timers accumulate on every `value` change. Rapid note switches create a growing backlog of stale timers, wasting resources and causing the test at `src/__tests__/editor-leak.test.tsx:26` to fail (`vi.getTimerCount()` would report 5 instead of ≤ 1). Fix: wrap the timeout in a cleanup by adding `const timerId = setTimeout(...)` and returning `return () => clearTimeout(timerId);` from the effect.

## Looks good

- The `setUnsavedFor` updater form (`prev => prev === noteId ? null : prev`) correctly guards against stale closures — if the note switches before the timer fires, it won't accidentally clear the new note's indicator.
- The comment explaining why the effect keys off `value` only (not `noteId`) is a thoughtful design decision; re-arming on every prop change would indeed feel jittery.
- The test is well-targeted: rapid `rerender` calls with different note IDs/values directly validate the timer-leak invariant.

## Open questions

- Should `noteId` be added to the `useEffect` dependency array? Currently, if `noteId` were to change without `value` changing, the pending timer callback would still reference the old `noteId`. This is unlikely in the current usage (each note has its own `value`) but could become a risk during future refactors.
- Are there CSS styles for `.editor__wrap` and `.editor__unsaved` defined elsewhere, or is that out of scope for this branch?
