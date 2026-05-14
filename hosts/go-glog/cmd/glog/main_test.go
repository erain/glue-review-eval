package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRun_StdinFiltersByLevel(t *testing.T) {
	in := strings.NewReader(strings.Join([]string{
		`{"level":"info","msg":"a"}`,
		`{"level":"debug","msg":"b"}`,
		`{"level":"error","msg":"c"}`,
	}, "\n") + "\n")
	var out, errb bytes.Buffer
	code := run([]string{"--level", "info,error"}, in, &out, &errb)
	if code != 0 {
		t.Fatalf("exit=%d stderr=%s", code, errb.String())
	}
	got := out.String()
	if !strings.Contains(got, "INFO a") || !strings.Contains(got, "ERROR c") {
		t.Errorf("missing lines: %q", got)
	}
	if strings.Contains(got, "DEBUG") {
		t.Errorf("debug leaked: %q", got)
	}
}

func TestRun_FileJSONOut(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "log")
	body := `{"level":"info","msg":"x"}` + "\n" + `not json` + "\n"
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	var out, errb bytes.Buffer
	code := run([]string{"--out", "json", path}, nil, &out, &errb)
	if code != 0 {
		t.Fatalf("exit=%d stderr=%s", code, errb.String())
	}
	// json mode re-emits raw lines verbatim, including non-JSON.
	if out.String() != body {
		t.Errorf("got %q want %q", out.String(), body)
	}
}

func TestRun_GrepAndField(t *testing.T) {
	in := strings.NewReader(strings.Join([]string{
		`{"level":"info","msg":"hello","user":"alice"}`,
		`{"level":"info","msg":"hello","user":"bob"}`,
		`{"level":"info","msg":"world","user":"alice"}`,
	}, "\n") + "\n")
	var out, errb bytes.Buffer
	code := run([]string{"--grep", "hello", "--field", "user=alice"}, in, &out, &errb)
	if code != 0 {
		t.Fatalf("exit=%d stderr=%s", code, errb.String())
	}
	got := out.String()
	if strings.Count(got, "\n") != 1 || !strings.Contains(got, "user=alice") {
		t.Errorf("unexpected output: %q", got)
	}
}

func TestRun_BadFlag(t *testing.T) {
	var out, errb bytes.Buffer
	code := run([]string{"--since", "nope"}, strings.NewReader(""), &out, &errb)
	if code == 0 {
		t.Fatal("expected non-zero exit")
	}
}

func TestRun_FollowRequiresFile(t *testing.T) {
	var out, errb bytes.Buffer
	code := run([]string{"-f"}, strings.NewReader(""), &out, &errb)
	if code != 2 {
		t.Fatalf("exit=%d", code)
	}
	if !strings.Contains(errb.String(), "requires a file") {
		t.Errorf("stderr=%q", errb.String())
	}
}

func TestRun_MissingFile(t *testing.T) {
	var out, errb bytes.Buffer
	code := run([]string{"/no/such/file"}, strings.NewReader(""), &out, &errb)
	if code == 0 {
		t.Fatal("expected non-zero exit")
	}
}

func TestRun_TooManyArgs(t *testing.T) {
	var out, errb bytes.Buffer
	code := run([]string{"a", "b"}, strings.NewReader(""), &out, &errb)
	if code != 2 {
		t.Fatalf("exit=%d", code)
	}
}
