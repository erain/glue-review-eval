Let me check the usage of these functions for more context.Let me check a couple more files for full context.## Summary

This branch loosens types in `useNotes.ts` and `storage.ts` to prepare for future rich-text support — `updateBody` and `saveState` now accept `any` instead of strict `string`/`StoredState` types, and `normalize` drops an intermediate cast.

## Issues

- [major] src/storage.ts:77 — `coerceNote` still validates `typeof n.body !== 'string'` and returns `null`, but `updateBody` now accepts `body: any` and will persist non-string values to localStorage. On reload, those notes will be silently dropped. This is a data-loss bug once any caller passes a non-string body. Fix: In `src/storage.ts`, update `coerceNote` to accept non-string body values (e.g., coerce them to string via `JSON.stringify` or allow `any` through) so notes with structured bodies survive a reload.

- [minor] src/hooks/useNotes.ts:59 — The `.map((n: any) => ...)` injects an `any` cast where `prev.notes` is already typed as `Note[]`. This suppresses legitimate type-checking inside the map callback. Fix: Remove the `: any` annotation from `n` in the `.map` callback so TypeScript can still validate property access.

- [minor] src/storage.ts:19 — `saveState` accepts `state: any` but the only current caller (`useDebouncedEffect` via `useNotes.ts`) always passes a full `StoredState`. The loosening is preemptive with no existing consumer needing it, and it removes compile-time safety at the boundary. Fix: Either revert `saveState` to accept `StoredState` until a partial-patch caller exists, or add an overload that accepts `Partial<StoredState>` and merges it with `EMPTY` before persisting.

## Looks good

- The `normalize` function simplification (removing the intermediate `obj` variable) is clean — the field-level validation below already does the safety work.
- The comment on `updateBody` explaining the intent for rich-text is appropriate forward-looking documentation.
- Error handling and the debounced persistence pattern are unchanged and remain sound.

## Open questions

- Is the `body: any` widening intended to be used by any *current* callers, or is it purely preparatory for a future rich-text feature? If purely future, it may be better to keep `string` and widen only when the consumer exists.
- If structured (non-string) bodies are persisted, what is the intended reload behavior? Should `coerceNote` be updated to serialize/parse them, or should a separate normalization step be added?
