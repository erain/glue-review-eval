// Package entry parses JSON-line log records.
package entry

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"
)

// Entry is one parsed log line. Raw holds the original bytes (without trailing
// newline) so callers can re-emit or regex-match against the verbatim input.
type Entry struct {
	Raw    string
	Fields map[string]any
	TS     time.Time
	HasTS  bool
	Level  string
	Msg    string
	// Parsed is false when the line was not valid JSON. In that case Fields
	// is nil and TS/Level/Msg are zero values.
	Parsed bool
}

// Parse decodes a single line. Lines that fail JSON parsing return an Entry
// with Parsed=false and the raw text preserved; this is not an error because
// raw lines are still useful to grep-style filters.
func Parse(line string) Entry {
	e := Entry{Raw: line}

	// Fast reject: anything that doesn't start with '{' is treated as raw.
	// Strict JSON only — we don't bother with arrays or scalars at the top.
	if len(line) == 0 || line[0] != '{' {
		return e
	}

	var m map[string]any
	if err := json.Unmarshal([]byte(line), &m); err != nil {
		return e
	}
	e.Fields = m
	e.Parsed = true

	if v, ok := m["level"].(string); ok {
		e.Level = v
	}
	if v, ok := m["msg"].(string); ok {
		e.Msg = v
	} else if v, ok := m["message"].(string); ok {
		e.Msg = v
	}
	if ts, ok := parseTS(m["ts"]); ok {
		e.TS = ts
		e.HasTS = true
	} else if ts, ok := parseTS(m["time"]); ok {
		e.TS = ts
		e.HasTS = true
	}
	return e
}

func parseTS(v any) (time.Time, bool) {
	switch x := v.(type) {
	case string:
		if t, err := time.Parse(time.RFC3339Nano, x); err == nil {
			return t, true
		}
		if t, err := time.Parse(time.RFC3339, x); err == nil {
			return t, true
		}
		// Allow bare unix-seconds-as-string for tolerance.
		if f, err := strconv.ParseFloat(x, 64); err == nil {
			return unixFloat(f), true
		}
	case float64:
		return unixFloat(x), true
	case json.Number:
		if f, err := x.Float64(); err == nil {
			return unixFloat(f), true
		}
	}
	return time.Time{}, false
}

func unixFloat(f float64) time.Time {
	sec := int64(f)
	nsec := int64((f - float64(sec)) * 1e9)
	return time.Unix(sec, nsec).UTC()
}

// FieldString returns a top-level field as a string for equality matching.
// Numbers and bools are stringified in a predictable way; everything else
// falls back to fmt.Sprint, which is good enough for "key=val" filtering.
func (e Entry) FieldString(key string) (string, bool) {
	if !e.Parsed {
		return "", false
	}
	v, ok := e.Fields[key]
	if !ok {
		return "", false
	}
	switch x := v.(type) {
	case string:
		return x, true
	case bool:
		return strconv.FormatBool(x), true
	case float64:
		// Render integers without a trailing ".0" so `id=42` matches.
		if x == float64(int64(x)) {
			return strconv.FormatInt(int64(x), 10), true
		}
		return strconv.FormatFloat(x, 'f', -1, 64), true
	case nil:
		return "", true
	default:
		return fmt.Sprint(x), true
	}
}
