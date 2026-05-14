The diff is a clean refactor — keyboard shortcut logic extracted from `App.tsx` into a new `useShortcuts` hook with identical behavior. Let me check for existing test coverage.## glue-review

No concerns — LGTM.

Mechanical extraction of keyboard shortcut logic from `App.tsx` into a dedicated `useShortcuts` hook. No behavior change — same modifier check (`metaKey || ctrlKey`), same key handling (`n` / `s`), same cleanup via `removeEventListener`. The new hook is properly typed with a `ShortcutHandlers` interface and follows the existing pattern (`useEffect` with cleanup return).
