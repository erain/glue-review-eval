## Summary

Extracts the inline reserved-key filtering logic in `render/render.go` into a standalone `nonReservedKeys` helper function. Behavior is unchanged.

## Looks good

- The refactor is mechanical and preserves identical behavior: same map lookup, same allocation hint (`len(e.Fields)`), same iteration order (random, but sorted afterward by the caller).
- The function is unexported, which is correct since it's only used once in this file.
- The doc comment on `nonReservedKeys` accurately describes what it does and notes that callers are responsible for sorting.

No issues or suggestions — this is a clean, safe refactor.
