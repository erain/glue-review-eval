## Summary

Adds a `useColorScheme` hook that reads the OS `prefers-color-scheme` media query and exposes the result on `<html data-theme="...">` so CSS can react to system theme changes without each component calling `matchMedia` directly.

## Issues

No bugs or correctness issues found. The SSR guards, cleanup logic, and dependency arrays are all correct.

## Suggestions

- [minor] `src/hooks/useColorScheme.ts:28` — The comment mentions that older Safari may need `addListener`, but the code only calls `addEventListener`. Either add a fallback to `addListener` for broader compatibility or soften the comment to avoid implying support that isn't implemented.

- [minor] `src/App.tsx:27` — The `typeof document !== 'undefined'` guard inside `useEffect` is redundant. `useEffect` never runs during SSR, so `document` is always defined when this code executes. It can be simplified to just `document.documentElement.dataset.theme = scheme;`.

## Looks good

- Clean separation of concerns with a dedicated, reusable hook.
- SSR-safe: `read()` guards against missing `window`/`matchMedia`.
- Proper cleanup of the `matchMedia` listener in the effect return.
- Minimal, targeted change — only two files touched.

## Open questions

- Should the hook also export a `setColorScheme` action to force a theme override (e.g., user toggles dark/light manually), or is OS-only detection intentional for now?
