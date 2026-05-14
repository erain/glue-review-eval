// Package tail streams lines from a growing file.
package tail

import (
	"bufio"
	"context"
	"io"
	"os"
	"time"
)

// PollInterval is how long to sleep between EOF re-reads in Follow.
var PollInterval = 200 * time.Millisecond

// Lines reads the reader line-by-line and emits each line (without trailing
// newline) on the returned channel. The channel closes on EOF or ctx cancel.
// Errors other than io.EOF are dropped silently — callers that need them
// should use bufio directly.
func Lines(ctx context.Context, r io.Reader) <-chan string {
	out := make(chan string, 64)
	go func() {
		defer close(out)
		br := bufio.NewReader(r)
		for {
			line, err := br.ReadString('\n')
			if len(line) > 0 {
				line = trimNewline(line)
				select {
				case out <- line:
				case <-ctx.Done():
					return
				}
			}
			if err != nil {
				return
			}
		}
	}()
	return out
}

// Follow opens path and streams its lines, continuing to read past EOF as the
// file grows (tail -f). It does not handle rotation. The channel closes when
// ctx is cancelled or the file is removed.
func Follow(ctx context.Context, path string) (<-chan string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	out := make(chan string, 64)
	go func() {
		defer close(out)
		defer f.Close()
		br := bufio.NewReader(f)
		var pending []byte
		for {
			if ctx.Err() != nil {
				return
			}
			line, err := br.ReadBytes('\n')
			if len(line) > 0 {
				pending = append(pending, line...)
				if line[len(line)-1] == '\n' {
					emit := trimNewline(string(pending))
					pending = pending[:0]
					select {
					case out <- emit:
					case <-ctx.Done():
						return
					}
					continue
				}
			}
			if err == io.EOF {
				// Detect deletion as a stop condition; without this Follow
				// would spin forever on a vanished file.
				if _, statErr := os.Stat(path); statErr != nil {
					return
				}
				select {
				case <-time.After(PollInterval):
				case <-ctx.Done():
					return
				}
				continue
			}
			if err != nil {
				return
			}
		}
	}()
	return out, nil
}

func trimNewline(s string) string {
	n := len(s)
	if n > 0 && s[n-1] == '\n' {
		s = s[:n-1]
	}
	if n := len(s); n > 0 && s[n-1] == '\r' {
		s = s[:n-1]
	}
	return s
}
