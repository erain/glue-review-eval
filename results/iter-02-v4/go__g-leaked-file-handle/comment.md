## glue-review

No concerns — LGTM.

The fix removes a race-prone double-close of `*os.File` in the file-path branch of `openSource`. Previously the cleanup function called `f.Close()` while `tail.Lines` still owned the reader in its goroutine; the fix replaces that with `noop` since `tail.Lines` closes the reader when it finishes. The new leak test verifies the FD count stays bounded over 50 iterations.
