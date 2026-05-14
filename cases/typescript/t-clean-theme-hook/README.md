# t-clean-theme-hook

**Category:** clean - **Severity:** none - **Host:** ts-notepad

A small, well-scoped improvement: a new `useColorScheme` hook reads
`prefers-color-scheme: dark` via `window.matchMedia`, listens for
system changes, and returns `'dark' | 'light'`. `App.tsx` consumes
it to set `<html data-theme="...">` so theming can be expressed in
plain CSS.

Nothing is broken. The hook guards `window`/`matchMedia` for SSR,
attaches and detaches the change listener correctly, and the App
wiring is a one-line side effect. Existing tests pass unchanged.

False-positive guards: don't claim a memory leak (the listener is
removed in the effect's cleanup), don't claim a hydration race (the
hook defaults to `'light'` when `window` is undefined), and don't
claim an XSS surface (no user-controlled markup is rendered).
