// Package filter decides which log entries to keep.
package filter

import (
	"regexp"
	"strings"
	"time"

	"github.com/erain/glog/entry"
)

// Filter is a set of predicates AND-ed together. A zero Filter matches
// everything. Construct via the New* helpers or by setting fields directly.
type Filter struct {
	Levels  map[string]struct{} // lowercased; nil means "any"
	Since   time.Time           // zero means "no lower bound"
	Until   time.Time           // zero means "no upper bound"
	Grep    *regexp.Regexp      // nil means "no regex"
	Fields  map[string]string   // key=value exact match on parsed JSON
	needsTS bool
}

// New builds a Filter from raw flag inputs. Now is injected so callers can
// pin time in tests; pass time.Now() in production.
func New(levels, grep string, fields []string, since, until time.Duration, now time.Time) (*Filter, error) {
	f := &Filter{}

	if levels = strings.TrimSpace(levels); levels != "" {
		f.Levels = map[string]struct{}{}
		for _, l := range strings.Split(levels, ",") {
			l = strings.ToLower(strings.TrimSpace(l))
			if l == "" {
				continue
			}
			f.Levels[l] = struct{}{}
		}
	}

	if grep != "" {
		re, err := regexp.Compile(grep)
		if err != nil {
			return nil, err
		}
		f.Grep = re
	}

	if len(fields) > 0 {
		f.Fields = map[string]string{}
		for _, kv := range fields {
			k, v, ok := strings.Cut(kv, "=")
			if !ok {
				return nil, &fieldErr{kv}
			}
			f.Fields[k] = v
		}
	}

	if since > 0 {
		f.Since = now.Add(-since)
		f.needsTS = true
	}
	if until > 0 {
		f.Until = now.Add(-until)
		f.needsTS = true
	}
	return f, nil
}

// Match reports whether the entry passes every active predicate. Unparsed
// entries pass filters that only need raw bytes (grep) but fail any filter
// that needs structured data.
func (f *Filter) Match(e entry.Entry) bool {
	if f == nil {
		return true
	}

	if f.Grep != nil && !f.Grep.MatchString(e.Raw) {
		return false
	}

	// Anything below needs parsed JSON; bail if we don't have it.
	structured := len(f.Levels) > 0 || len(f.Fields) > 0 || f.needsTS
	if structured && !e.Parsed {
		return false
	}

	if len(f.Levels) > 0 {
		if _, ok := f.Levels[strings.ToLower(e.Level)]; !ok {
			return false
		}
	}

	if f.needsTS {
		if !e.HasTS {
			return false
		}
		// --since N: keep entries no older than N ago (TS >= now-since).
		if !f.Since.IsZero() && e.TS.Before(f.Since) {
			return false
		}
		// --until N: keep entries at least N old (TS <= now-until).
		if !f.Until.IsZero() && e.TS.After(f.Until) {
			return false
		}
	}

	for k, want := range f.Fields {
		got, ok := e.FieldString(k)
		if !ok || got != want {
			return false
		}
	}
	return true
}

type fieldErr struct{ raw string }

func (e *fieldErr) Error() string { return "field filter must be key=value: " + e.raw }
