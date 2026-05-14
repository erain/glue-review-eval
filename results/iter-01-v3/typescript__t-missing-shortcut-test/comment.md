## glue-review

No concerns — LGTM.

Clean extraction of inline keyboard shortcut logic into a dedicated `useShortcuts` hook. The behavior is identical to the previous inline `useEffect` in `App.tsx` — same event listener, same dependencies, same cleanup. The `ShortcutHandlers` interface is well-defined and the hook follows React naming conventions.
