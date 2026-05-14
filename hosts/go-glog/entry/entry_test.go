package entry

import (
	"testing"
	"time"
)

func TestParse_HappyJSON(t *testing.T) {
	line := `{"ts":"2024-01-02T03:04:05Z","level":"info","msg":"hello","user":"alice","id":42}`
	e := Parse(line)
	if !e.Parsed {
		t.Fatal("expected parsed")
	}
	if e.Level != "info" {
		t.Errorf("level=%q", e.Level)
	}
	if e.Msg != "hello" {
		t.Errorf("msg=%q", e.Msg)
	}
	if !e.HasTS {
		t.Fatal("expected ts")
	}
	want := time.Date(2024, 1, 2, 3, 4, 5, 0, time.UTC)
	if !e.TS.Equal(want) {
		t.Errorf("ts=%v want %v", e.TS, want)
	}
	if v, ok := e.FieldString("user"); !ok || v != "alice" {
		t.Errorf("user=%q ok=%v", v, ok)
	}
	if v, ok := e.FieldString("id"); !ok || v != "42" {
		t.Errorf("id=%q ok=%v", v, ok)
	}
}

func TestParse_RawPassthrough(t *testing.T) {
	for _, line := range []string{
		"not json",
		"",
		"{broken",
		"[]",
	} {
		e := Parse(line)
		if e.Parsed {
			t.Errorf("expected raw for %q", line)
		}
		if e.Raw != line {
			t.Errorf("raw=%q want %q", e.Raw, line)
		}
	}
}

func TestParse_TSVariants(t *testing.T) {
	cases := []struct {
		line string
		want time.Time
	}{
		{`{"ts":"2024-01-02T03:04:05Z"}`, time.Date(2024, 1, 2, 3, 4, 5, 0, time.UTC)},
		{`{"ts":"2024-01-02T03:04:05.500Z"}`, time.Date(2024, 1, 2, 3, 4, 5, 500_000_000, time.UTC)},
		{`{"ts":1704164645}`, time.Unix(1704164645, 0).UTC()},
		{`{"time":"2024-01-02T03:04:05Z"}`, time.Date(2024, 1, 2, 3, 4, 5, 0, time.UTC)},
		{`{"ts":"1704164645"}`, time.Unix(1704164645, 0).UTC()},
	}
	for _, tc := range cases {
		e := Parse(tc.line)
		if !e.HasTS {
			t.Errorf("%s: no ts", tc.line)
			continue
		}
		if !e.TS.Equal(tc.want) {
			t.Errorf("%s: ts=%v want %v", tc.line, e.TS, tc.want)
		}
	}
}

func TestFieldString_Types(t *testing.T) {
	e := Parse(`{"s":"x","b":true,"n":3.14,"i":7,"z":null}`)
	cases := map[string]string{"s": "x", "b": "true", "n": "3.14", "i": "7", "z": ""}
	for k, want := range cases {
		got, ok := e.FieldString(k)
		if !ok {
			t.Errorf("%s missing", k)
			continue
		}
		if got != want {
			t.Errorf("%s=%q want %q", k, got, want)
		}
	}
	if _, ok := e.FieldString("nope"); ok {
		t.Error("missing key returned ok")
	}
}

func TestFieldString_Unparsed(t *testing.T) {
	e := Parse("not json")
	if _, ok := e.FieldString("anything"); ok {
		t.Error("unparsed should never report ok")
	}
}
