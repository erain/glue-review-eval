# t-rejected-context-everything

**Category:** rejected-direction - **Severity:** medium - **Host:** ts-notepad

Introduces a global `NotesContext`, wires the app through a
`NotesProvider` in `main.tsx`, and refactors `Editor` and `Preview` to
read the active note from `useNotesContext()` instead of receiving it
as props. Pitched as a fix for "prop drilling".

There is no prop drilling here. `useNotes` already centralises state
and `App.tsx` hands a handful of values to direct children (no
intermediate layers). The context adds a file, adds boilerplate at
every consumer, forces every render-in-isolation test to wrap a
provider, and removes the option to back multiple independent
notepads with `useNotes`.

Reviewer should reject the direction outright: revert the context,
keep `useNotes` direct, pass `selectedNote` and `updateBody` to
`Editor`/`Preview` as props as before. No-acceptance — there is no
test to make pass; the right outcome is a rollback recommendation.

False-positive guards: no memory leak, no XSS surface, no race
condition. The change is bad on design-clarity grounds alone.
