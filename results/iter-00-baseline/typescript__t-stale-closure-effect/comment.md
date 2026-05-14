Let me look at the surrounding code for more context on the `useNotes` hook.## Summary

Adds a save-on-window-blur safety net to `useNotes` so notes aren't lost if the user switches tabs during the debounce window.

## Issues

- [critical] `src/hooks/useNotes.ts:79` — The `useEffect` with `[]` captures `state` in a closure on mount, so `snapshot` is always the *initial* state. Every blur will persist stale data, not the current state. The test only passes because it dispatches blur synchronously inside `act` before React re-renders, masking the bug. Fix: use a `useRef` to hold the latest state and read from it in `onBlur`:

```ts
const stateRef = useRef(state);
stateRef.current = state; // keep ref current on every render

useEffect(() => {
  function onBlur() {
    saveState(stateRef.current);
  }
  window.addEventListener('blur', onBlur);
  return () => window.removeEventListener('blur', onBlur);
}, []);
```

## Open questions

- Does this need cleanup on unmount? (The `removeEventListener` in the effect return handles it.)
- The comment says "subsequent state changes are already covered by the debounced effect above" — but the whole point of this feature is to cover the debounce gap, so using a stale closure defeats that purpose.
