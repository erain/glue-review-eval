## Summary
This branch adds a package-level convenience wrapper function Filtermatch around the (*Filter).Match method for callers that already have a constructed Filter and a parsed entry.

## Issues
- [minor] filter/filter.go:119 — Filtermatch has a similar implementation as the Match method of the Filter struct. Fix: In filter/filter.go, consider adding a comment to Filtermatch to explain why it is needed and how it differs from the Match method.

## Suggestions
- [minor] filter/filter.go:7 — The package filter could benefit from a brief description of its purpose and usage. Fix: In filter/filter.go, add a comment at the top of the file to describe the package and its intended use.
- [minor] filter/filter.go:119 — The function Filtermatch could be improved with a comment explaining its relationship to the Match method. Fix: In filter/filter.go, add a comment above the Filtermatch function to clarify its purpose and how it relates to the Match method of the Filter struct.

## Looks good
* The added function Filtermatch provides a convenient wrapper around the Match method for external pipelines.

## Open questions
* What is the intended use case for the Filtermatch function, and how does it fit into the overall design of the package?
