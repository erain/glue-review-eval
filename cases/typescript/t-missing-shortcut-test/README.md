# t-missing-shortcut-test

**Category:** missing-test - **Severity:** medium - **Host:** ts-notepad

The PR extracts the global keyboard-shortcut wiring out of `App.tsx`
into a new `useShortcuts` hook at `src/hooks/useShortcuts.ts`. The
hook owns a real chunk of behaviour — Cmd/Ctrl mod detection, key
normalisation, two branches with `preventDefault` — but ships with no
test alongside it. There is no `App.test.tsx` either, so the keymap
logic is entirely uncovered.

This is a missing-test case: the reviewer should call out the
untested hook and direct the fix block to add a
`useShortcuts.test.ts` covering the Cmd+N → new-note and Cmd+S →
flush branches (and the Ctrl variant). No acceptance gate — the
existing tests still pass.
