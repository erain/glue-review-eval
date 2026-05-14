package tail

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestLines_ReaderToEOF(t *testing.T) {
	ctx := context.Background()
	r := strings.NewReader("a\nb\nc\n")
	ch := Lines(ctx, r)
	var got []string
	for line := range ch {
		got = append(got, line)
	}
	if strings.Join(got, ",") != "a,b,c" {
		t.Errorf("got %v", got)
	}
}

func TestLines_NoTrailingNewline(t *testing.T) {
	ch := Lines(context.Background(), strings.NewReader("a\nb"))
	var got []string
	for line := range ch {
		got = append(got, line)
	}
	if strings.Join(got, ",") != "a,b" {
		t.Errorf("got %v", got)
	}
}

func TestLines_StripsCarriageReturn(t *testing.T) {
	ch := Lines(context.Background(), strings.NewReader("a\r\nb\r\n"))
	var got []string
	for line := range ch {
		got = append(got, line)
	}
	if strings.Join(got, ",") != "a,b" {
		t.Errorf("got %v", got)
	}
}

func TestFollow_GrowingFile(t *testing.T) {
	prev := PollInterval
	PollInterval = 10 * time.Millisecond
	t.Cleanup(func() { PollInterval = prev })

	dir := t.TempDir()
	path := filepath.Join(dir, "log")
	f, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := f.WriteString("first\n"); err != nil {
		t.Fatal(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	ch, err := Follow(ctx, path)
	if err != nil {
		t.Fatal(err)
	}

	got := readN(t, ch, 1, time.Second)
	if got[0] != "first" {
		t.Errorf("got %q want first", got[0])
	}

	if _, err := f.WriteString("second\nthird\n"); err != nil {
		t.Fatal(err)
	}
	f.Close()

	got = readN(t, ch, 2, time.Second)
	if got[0] != "second" || got[1] != "third" {
		t.Errorf("got %v", got)
	}
}

func TestFollow_StopsOnDelete(t *testing.T) {
	prev := PollInterval
	PollInterval = 10 * time.Millisecond
	t.Cleanup(func() { PollInterval = prev })

	dir := t.TempDir()
	path := filepath.Join(dir, "log")
	if err := os.WriteFile(path, []byte("hi\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	ch, err := Follow(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	_ = readN(t, ch, 1, time.Second)

	if err := os.Remove(path); err != nil {
		t.Fatal(err)
	}
	select {
	case _, ok := <-ch:
		if ok {
			// Drain any final straggler then expect close.
			_, ok = <-ch
			if ok {
				t.Fatal("expected channel close after delete")
			}
		}
	case <-time.After(2 * time.Second):
		t.Fatal("Follow did not stop after delete")
	}
}

func readN(t *testing.T, ch <-chan string, n int, timeout time.Duration) []string {
	t.Helper()
	var got []string
	deadline := time.After(timeout)
	for len(got) < n {
		select {
		case s, ok := <-ch:
			if !ok {
				t.Fatalf("channel closed after %d lines, wanted %d", len(got), n)
			}
			got = append(got, s)
		case <-deadline:
			t.Fatalf("timeout after %d lines, wanted %d", len(got), n)
		}
	}
	return got
}
