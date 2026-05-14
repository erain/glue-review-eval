## glue-review

Type loosening trades compile-time safety for speculative flexibility — several `any` introductions weaken the type contract without equivalent runtime guards.

- **medium** — `src/hooks/useNotes.ts:18` — Changing `updateBody`'s `body` parameter from `string` to `any` drops type checking at every call site; the "rich-text someday" justification doesn't warrant losing current guarantees.
- **medium** — `src/storage.ts:48` — `saveState` accepting `any` instead of `StoredState` means a partial object passed without spreading `EMPTY` silently produces incomplete/corrupt persisted state.
- **high** — `src/storage.ts:63` — `normalize` changed from `unknown` to `any`; this function processes untrusted deserialized localStorage data, which is exactly where `unknown` is the correct defensive choice.
- **low** — `src/hooks/useNotes.ts:52` — The inline `.map((n: any) => ...)` cast to `any` is unnecessary; the prior `notes` array was already typed as `Note[]`.
- **low** — `src/storage.ts:79` — `value.notes` / `value.selectedId` accesses on the `any` parameter lose the intermediate `obj` variable that served as self-documenting proof of the cast.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **src/hooks/useNotes.ts:18** — `updateBody` parameter type reverted from `any` back to `string`.
   - Change `body: any` back to `body: string` in both the `UseNotesApi` interface (line 18) and the `useCallback` signature (line 52).
   - If rich-text support is planned, add a TODO comment or introduce a `string | RichTextNode` union — do not default to `any`.
   Acceptance: `tsc --noEmit` reports no type errors and `updateBody`'s parameter type is `string` in both the interface and implementation.

2. **src/storage.ts:48** — `saveState` parameter type reverted from `any` back to `StoredState`.
   - Restore the original `state: StoredState` type so callers must provide a complete state object.
   Acceptance: `tsc --noEmit` reports no type errors and `saveState`'s parameter type is `StoredState`.

3. **src/storage.ts:63** — `normalize` parameter type reverted from `any` back to `unknown`.
   - Restore `value: unknown` and the `const obj = value as Record<string, unknown>` cast that was removed.
   - This is the function handling untrusted storage input — `unknown` is the correct defensive type.
   Acceptance: `tsc --noEmit` reports no type errors and `normalize`'s parameter type is `unknown`; the `obj` intermediate variable is restored.

4. **src/hooks/useNotes.ts:52** — Remove the `: any` annotation from the `.map()` callback parameter.
   - The array is already typed as `Note[]`; a typed callback parameter is redundant.
   Acceptance: `tsc --noEmit` reports no type errors and the `.map` callback has no `any` annotation.

5. **src/storage.ts:79** — Remove the `: any` annotation from `.map((n: any) => ...)` inside `normalize`.
   - Same rationale: the array is already typed after `coerceNote` filtering.
   Acceptance: `tsc --noEmit` reports no type errors and the map callback has no `any` annotation.
```
