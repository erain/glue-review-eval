package filter

import (
	"testing"
	"time"

	"github.com/erain/glog/entry"
)

func mustFilter(t *testing.T, level, grep string, fields []string, since, until time.Duration, now time.Time) *Filter {
	t.Helper()
	f, err := New(level, grep, fields, since, until, now)
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	return f
}

func TestMatch_Level(t *testing.T) {
	now := time.Now()
	f := mustFilter(t, "info,Error", "", nil, 0, 0, now)

	cases := []struct {
		line string
		want bool
	}{
		{`{"level":"info","msg":"hi"}`, true},
		{`{"level":"INFO"}`, true},
		{`{"level":"error"}`, true},
		{`{"level":"debug"}`, false},
		{`{"msg":"no level"}`, false},
		{`not json`, false},
	}
	for _, tc := range cases {
		if got := f.Match(entry.Parse(tc.line)); got != tc.want {
			t.Errorf("%s -> %v want %v", tc.line, got, tc.want)
		}
	}
}

func TestMatch_Grep(t *testing.T) {
	f := mustFilter(t, "", `"user":"al`, nil, 0, 0, time.Now())
	if !f.Match(entry.Parse(`{"user":"alice"} extra`)) {
		t.Error("expected match on raw substring")
	}
	if f.Match(entry.Parse(`{"user":"bob"}`)) {
		t.Error("expected no match")
	}
	// grep on unparsed line should still apply.
	f2 := mustFilter(t, "", `user=alice`, nil, 0, 0, time.Now())
	if !f2.Match(entry.Parse(`raw line user=alice`)) {
		t.Error("grep should run on raw line")
	}
}

func TestMatch_Field(t *testing.T) {
	f := mustFilter(t, "", "", []string{"user=alice", "id=42"}, 0, 0, time.Now())
	if !f.Match(entry.Parse(`{"user":"alice","id":42,"x":"y"}`)) {
		t.Error("expected match")
	}
	if f.Match(entry.Parse(`{"user":"alice","id":43}`)) {
		t.Error("expected mismatch on id")
	}
	if f.Match(entry.Parse(`{"user":"alice"}`)) {
		t.Error("missing key should not match")
	}
}

func TestMatch_TimeRange(t *testing.T) {
	now := time.Date(2024, 6, 1, 12, 0, 0, 0, time.UTC)
	// Window: from 1h ago up to 5m ago, i.e. --since 1h --until 5m.
	f := mustFilter(t, "", "", nil, time.Hour, 5*time.Minute, now)

	in := now.Add(-30 * time.Minute)
	tooNew := now.Add(-2 * time.Minute)
	tooOld := now.Add(-2 * time.Hour)

	mk := func(ts time.Time) entry.Entry {
		return entry.Entry{Raw: "x", Parsed: true, HasTS: true, TS: ts, Fields: map[string]any{}}
	}
	if !f.Match(mk(in)) {
		t.Error("in-window rejected")
	}
	if f.Match(mk(tooNew)) {
		t.Error("too-new accepted")
	}
	if f.Match(mk(tooOld)) {
		t.Error("too-old accepted")
	}
	// No ts and a time-bound filter -> reject.
	if f.Match(entry.Parse(`{"msg":"no ts"}`)) {
		t.Error("missing ts should fail time filter")
	}
}

func TestNew_BadField(t *testing.T) {
	_, err := New("", "", []string{"oops"}, 0, 0, time.Now())
	if err == nil {
		t.Fatal("expected error for malformed field")
	}
}

func TestNew_BadRegex(t *testing.T) {
	_, err := New("", "(", nil, 0, 0, time.Now())
	if err == nil {
		t.Fatal("expected regex error")
	}
}

func TestZeroFilterMatchesEverything(t *testing.T) {
	var f *Filter
	if !f.Match(entry.Parse("anything")) {
		t.Error("nil filter should match")
	}
	f2 := &Filter{}
	if !f2.Match(entry.Parse("anything")) {
		t.Error("zero filter should match")
	}
}

func TestParseDuration(t *testing.T) {
	cases := []struct {
		in   string
		want time.Duration
		err  bool
	}{
		{"", 0, false},
		{"5m", 5 * time.Minute, false},
		{"2h30m", 2*time.Hour + 30*time.Minute, false},
		{"1500ms", 1500 * time.Millisecond, false},
		{"abc", 0, true},
	}
	for _, tc := range cases {
		got, err := ParseDuration(tc.in)
		if tc.err {
			if err == nil {
				t.Errorf("%q: expected error", tc.in)
			}
			continue
		}
		if err != nil {
			t.Errorf("%q: %v", tc.in, err)
			continue
		}
		if got != tc.want {
			t.Errorf("%q: got %v want %v", tc.in, got, tc.want)
		}
	}
}
