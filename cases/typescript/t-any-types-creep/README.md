# t-any-types-creep

**Category:** style - **Severity:** low - **Host:** ts-notepad

Three small, individually-defensible "the types were getting in the
way" changes that collectively erode the type-safety of the store
boundary:

1. `saveState(state: any, ...)` in `src/storage.ts` — was `StoredState`.
2. `normalize(value: any)` (and a `(n: any) =>` callback) in the same
   file — was `unknown` with an explicit `Record<string, unknown>`
   narrowing.
3. `updateBody(id: string, body: any)` in `src/hooks/useNotes.ts`
   (signature, interface field, and the inner map callback) — was
   `string`.

Existing tests still pass and `tsc -b --noEmit` is clean; that is the
point of the case. Reviewer should flag the three `any`s and direct
the fix block to restore the original `StoredState` / `unknown` /
`string` signatures without introducing new casts at the callsites.
No new failing acceptance test — this is a type-discipline lint, not
a behaviour bug.
