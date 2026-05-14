## glue-review

No concerns — LGTM.

Pure refactor extracting an inline loop into a `nonReservedKeys` helper. No behavior change, existing tests cover the same paths, and the new function is documented.
