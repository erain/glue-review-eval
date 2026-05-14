## Summary

This branch removes the `key={note.id}` prop from the `<li>` elements in `NoteList.tsx`'s `.map()` and adds a test asserting no missing-key warnings are emitted. The rationale is that notes are sorted by `updatedAt` desc upstream, so the iteration order is stable.

## Issues

- [major] src/components/NoteList.tsx:41 — Removing `key={note.id}` is a correctness risk. The component supports `onDelete(id)`, so items can be removed from the middle of the list. It also sorts by `updatedAt` desc, so updating a note's timestamp can reorder it. Without explicit keys, React falls back to index-based reconciliation, which will misalign DOM nodes with data when items are deleted or reordered — leading to subtle rendering bugs (stale state on the wrong row, incorrect aria-selected associations, etc.). Fix: Restore `key={note.id}` on the `<li>` element.

- [minor] src/__tests__/NoteList.keys.test.tsx:1 — The test only verifies the absence of console warnings; it does not test actual rendering correctness after deletion or reordering. If keys are intentionally removed, the test coverage is insufficient to catch the resulting bugs. Fix: Either delete this test (since it guards a regression rather than a feature) or add rendering/mutation tests that verify the correct note remains selected after deleting a different note.

## Open questions

- Is there an upstream mechanism (e.g., stable note objects by reference, immutable list replacement) that guarantees the array order is truly stable across renders even after deletions and timestamp updates? If so, a comment pointing to that invariant would be needed to justify dropping the key.
