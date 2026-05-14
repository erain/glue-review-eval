# t-multi-effect-and-leak

**Category:** multi-bug - **Severity:** high - **Host:** ts-notepad

Adds an "unsaved" pip next to the textarea that flashes when the user
types and quietly hides itself after `UNSAVED_FLASH_MS`. The
implementation in `src/components/Editor.tsx` carries two independent
bugs in the same `useEffect`:

1. The effect closes over `noteId` inside the `setTimeout` callback
   but lists only `[value]` in its dependency array. When the user
   switches notes mid-flash, the pending timer fires with the old
   `noteId` and can clear the indicator on the wrong note.
2. The `setTimeout` handle is never captured, so the effect's cleanup
   does not call `clearTimeout`. Each `value` change arms a fresh
   timer while the old one keeps ticking; rapid note-switching leaks
   N timers and triggers React strict-mode's double-invoke warnings
   in dev.

The acceptance test re-renders `Editor` with five different
`noteId`/`value` pairs and asserts `vi.getTimerCount() <= 1`. Buggy
code leaks five timers; the fix requires both adding `noteId` to the
deps array and returning `() => clearTimeout(timer)` from the effect.

Reviewer's fix block must contain at least two items — fixing only
the leak or only the deps leaves the other bug live.
