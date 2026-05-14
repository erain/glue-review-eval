## glue-review

No concerns — LGTM.

The change is a pure mechanical extraction: an inline loop is moved into a `nonReservedKeys` helper with the same filtering logic and identical caller behavior (sort + iterate). No behavioral change, no new imports, no test gaps.
