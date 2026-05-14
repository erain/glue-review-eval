## Summary
This branch makes the JSON parser in the entry package more tolerant of lines with prefixes, allowing them to be parsed as best-effort raw lines.

## Issues
- [major] entry/entry.go:24 — The `Parse` function does not handle the case where the input line is empty. Fix: In entry/entry.go, add a check at the beginning of the `Parse` function to return an `Entry` with `Parsed` set to `false` when the input line is empty.
- [minor] entry/entry.go:45 — The `parseTS` function does not handle the case where the timestamp is in a format other than RFC3339 or RFC3339Nano. Fix: In entry/entry.go, add more time formats to the `parseTS` function to handle different timestamp formats.

## Suggestions
- [minor] entry/entry.go:10 — The `Entry` struct has a `Parsed` field that is not used consistently throughout the package. Fix: In entry/entry.go, remove the `Parsed` field from the `Entry` struct and instead use a separate function to check if an `Entry` has been parsed.
- [minor] entry/entry.go:20 — The `Parse` function does not handle the case where the input line is too large. Fix: In entry/entry.go, add a check at the beginning of the `Parse` function to return an error when the input line is too large.

## Looks good
* The `Parse` function now correctly handles lines with prefixes.
* The `parseTS` function now correctly handles timestamps in different formats.

## Open questions
* How will the `Entry` struct be used in the rest of the package?
* What are the performance implications of using a more tolerant parser?
