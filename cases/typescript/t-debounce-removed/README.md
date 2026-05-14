# t-debounce-removed

**Category:** perf - **Severity:** medium - **Host:** ts-notepad

`useNotes` previously persisted to `localStorage` through a 300 ms
debounce so bursts of keystrokes collapsed into a single write. The PR
unwraps the call into a plain `useEffect`, claiming the timer is
unnecessary ("localStorage writes are fast"). Each keystroke now
serialises and writes the full notes corpus.

The new `src/__tests__/persistence-debounce.test.ts` simulates ten
rapid edits in separate `act()` ticks and asserts at most two
`localStorage.setItem` calls; the buggy code produces ten. The PR also
loosens two existing useNotes tests that previously asserted the
"nothing persisted right after create" behaviour — a correct fix
should restore those assertions alongside the debounce.
