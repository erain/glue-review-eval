## glue-review

New `useColorScheme` hook added with no test coverage.

- **medium** — `src/hooks/useColorScheme.ts` (entire file) — New hook exports behavior (`read()`, `matchMedia` subscription, SSR fallback) but no test file exists to verify any of it.
- **medium** — `src/App.tsx:24-28` — The `data-theme` side-effect on `<html>` is new runtime behavior with no integration test asserting the attribute is set correctly.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/hooks/useColorScheme.ts** (new test file `tests/useColorScheme.test.tsx`) — The new hook has zero test coverage.
   - Write a test that mocks `window.matchMedia` and asserts `useColorScheme()` returns `'dark'` when `prefers-color-scheme: dark` matches and `'light'` when it does not.
   - Write a test that simulates a media-query change event and asserts the hook state updates reactively.
   - Write a test that runs in a JSDOM-only environment (no `matchMedia`) and asserts the hook returns the SSR-safe default `'light'` without crashing.
   Acceptance: `npx jest tests/useColorScheme.test.tsx --no-coverage` passes (all cases green).

2. **src/App.tsx** (new test file `tests/AppColorScheme.test.tsx`) — No integration test for the `data-theme` side-effect.
   - Render `<App />` (or just the relevant subtree) and assert that `document.documentElement.dataset.theme` is set to the color scheme value after the effect runs.
   - Mock `useColorScheme` to return `'dark'` and assert `dataset.theme` becomes `'dark'`, then mock `'light'` and assert it updates.
   Acceptance: `npx jest tests/AppColorScheme.test.tsx --no-coverage` passes.
```
