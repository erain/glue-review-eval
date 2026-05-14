## Summary
This branch refactors the render package to extract a nonReservedKeys helper.

## Issues
- [minor] render/render.go:77 — The new nonReservedKeys function has a comment that says "Callers sort the result themselves", but the Render function in the same file does not sort the keys before using them. Fix: In render/render.go, add a call to sort.Strings after getting the keys from nonReservedKeys, like this: keys := nonReservedKeys(e); sort.Strings(keys).

## Suggestions
- [minor] render/render.go:0 — The nonReservedKeys function could be improved by using a more efficient data structure, such as a map, to store the reserved keys. Fix: In render/render.go, replace the reservedKeys map with a struct that has a method to check if a key is reserved, like this: type reservedKeySet struct { m map[string]struct{} }; func (r *reservedKeySet) contains(key string) bool { _, ok := r.m[key]; return ok }; var reservedKeys = &reservedKeySet{m: map[string]struct{}{"ts": {}, "time": {}, "level": {}, "msg": {}, "message": {}}}.
- [minor] render/render.go:83 — The quoteIfNeeded function could be improved by using a more efficient way to check if a string needs to be quoted. Fix: In render/render.go, replace the quoteIfNeeded function with a simpler implementation that uses the strings.ContainsAny function, like this: func quoteIfNeeded(s string) string { if strings.ContainsAny(s, " \t\n\"") { return fmt.Sprintf("%q", s) }; return s }.

## Looks good
* The refactored code is more readable and maintainable.
* The new nonReservedKeys function is a good extraction of a common operation.

## Open questions
* What is the purpose of the nonReservedKeys function and how is it used in the render package?
* How does the quoteIfNeeded function work and what are its implications for the rendering of entries?
