# t-stale-closure-effect

**Category:** logic-bug - **Severity:** high - **Host:** ts-notepad

`useNotes` gains a window-blur safety net that flushes the current
notes state to localStorage when the user switches tabs. The new
`useEffect` is wired with an empty dependency array and copies `state`
into a local `snapshot` constant before binding the listener. The
closure inside `onBlur` therefore keeps pointing at the mount-time
state forever; later edits and newly-created notes never make it into
the blur-driven persistence path.

The acceptance test creates a note, performs two edit-and-blur cycles,
and asserts that the final edit is what `loadState` returns. With the
stale closure the persisted body is `undefined` (the mount-time
snapshot had no notes). The correct fix is to add `state` to the deps
array — or hold the latest state in a `useRef` updated on every render
— so the blur handler sees the live value.

False-positive guards: this is not an XSS case, not a quota race, and
the cleanup function does remove the listener correctly on unmount.
