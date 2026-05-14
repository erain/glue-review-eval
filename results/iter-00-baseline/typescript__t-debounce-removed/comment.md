## Summary

This branch removes the debounced localStorage persistence from `useNotes`, replacing it with an immediate `useEffect` that writes to localStorage on every state change, and simplifies the `flush` method accordingly.

## Issues

- [critical] `src/__tests__/persistence-debounce.test.ts`:0 — This new test file asserts that rapid edits are coalesced into at most 2 localStorage writes, but the debounce mechanism it tests has been removed. With the new `useEffect([state])` approach, each of the 10 `act(() => updateBody(...))` calls will trigger an independent `saveState`, producing 10 writes (not ≤2). **This test will fail.** Either delete the file or rewrite it to verify that writes happen synchronously with each state change. Fix: Delete `src/__tests__/persistence-debounce.test.ts` or rewrite it to assert that each `updateBody` call immediately triggers a `setItem` call (10 writes for 10 edits).

## Suggestions

- [minor] `src/hooks/useNotes.ts`:1 — The comment "localStorage writes are fast" is a reasonable justification, but consider noting the trade-off explicitly: removing debounce means every intermediate state (e.g., mid-keystroke) is persisted, which increases write volume in exchange for simpler code and a faster "saved" indicator.

## Looks good

- The `flush` refactor is clean — using `stateRef.current` inside a stable `useCallback` correctly avoids stale closures without needing the old debounce timer.
- Removing `PERSIST_DELAY_MS` and the `useDebouncedEffect` dependency is a good simplification; the existing `useNotes.test.ts` tests are correctly updated to no longer advance fake timers.

## Open questions

- Is the `useDebouncedEffect` hook (in `src/hooks/useDebounce.ts`) still used anywhere else, or is it now dead code?
