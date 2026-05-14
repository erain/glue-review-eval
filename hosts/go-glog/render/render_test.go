package render

import (
	"bytes"
	"strings"
	"testing"

	"github.com/erain/glog/entry"
)

func TestNew_Unknown(t *testing.T) {
	if _, err := New("yaml"); err == nil {
		t.Fatal("expected error for unknown format")
	}
}

func TestPlain_Parsed(t *testing.T) {
	r, _ := New("plain")
	e := entry.Parse(`{"ts":"2024-01-02T03:04:05Z","level":"info","msg":"hello world","user":"alice","id":42}`)
	var buf bytes.Buffer
	if err := r.Render(&buf, e); err != nil {
		t.Fatal(err)
	}
	got := buf.String()
	wantPrefix := "2024-01-02T03:04:05Z INFO hello world "
	if !strings.HasPrefix(got, wantPrefix) {
		t.Errorf("prefix mismatch: %q", got)
	}
	// Tail keys are alpha-sorted.
	if !strings.Contains(got, "id=42 user=alice") {
		t.Errorf("expected sorted key tail, got %q", got)
	}
	if !strings.HasSuffix(got, "\n") {
		t.Error("missing newline")
	}
}

func TestPlain_QuotesValuesWithSpaces(t *testing.T) {
	r, _ := New("plain")
	e := entry.Parse(`{"level":"info","msg":"m","who":"a b"}`)
	var buf bytes.Buffer
	_ = r.Render(&buf, e)
	if !strings.Contains(buf.String(), `who="a b"`) {
		t.Errorf("expected quoted value, got %q", buf.String())
	}
}

func TestPlain_Unparsed(t *testing.T) {
	r, _ := New("plain")
	var buf bytes.Buffer
	_ = r.Render(&buf, entry.Parse("not json"))
	if buf.String() != "not json\n" {
		t.Errorf("got %q", buf.String())
	}
}

func TestJSON_RawPassthrough(t *testing.T) {
	r, _ := New("json")
	raw := `{"level":"info","msg":"hi"}`
	var buf bytes.Buffer
	_ = r.Render(&buf, entry.Parse(raw))
	if buf.String() != raw+"\n" {
		t.Errorf("got %q", buf.String())
	}
}
