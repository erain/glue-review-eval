## glue-review

No concerns — LGTM.

Clean implementation: the `useColorScheme` hook correctly handles SSR via `typeof window` guards, uses a lazy `useState` initializer to avoid a flash, listens for `matchMedia` changes with proper cleanup, and the single `data-theme` attribute on `<html>` avoids scattering `matchMedia` reads across components.
