# g-leaked-file-handle

**Category:** logic-bug · **Severity:** medium · **Host:** go-glog

`openSource` in `cmd/glog/main.go` previously returned a cleanup func that
closed the `*os.File` opened for the input path. The PR drops that
cleanup, replacing it with `noop` and a comment claiming `tail.Lines` owns
the reader. The claim is wrong — `bufio.NewReader` does not close its
underlying `io.Reader`, so the file descriptor is leaked until the GC
finaliser runs.

`TestRun_FilePathDoesNotLeakFDs` invokes `run()` 50 times against a real
file and asserts the open-fd count (via `/proc/self/fd`) grows by no more
than 10. With the buggy code the count grows by 50; with the fix it stays
flat.

The reviewer should call out the leak, name `f.Close()` / `defer`, and
point at `cmd/glog/main.go`. Fix-directive: restore
`func() { f.Close() }` as the cleanup.
