// Package render formats entries for output.
package render

import (
	"fmt"
	"io"
	"sort"
	"strings"
	"time"

	"github.com/erain/glog/entry"
)

// Renderer writes entries to a sink.
type Renderer interface {
	Render(w io.Writer, e entry.Entry) error
}

// New returns a renderer for the named format. Unknown formats return an
// error rather than silently picking a default — bad flag input should be
// loud.
func New(format string) (Renderer, error) {
	switch format {
	case "plain", "":
		return plain{}, nil
	case "json":
		return rawJSON{}, nil
	default:
		return nil, fmt.Errorf("unknown output format %q", format)
	}
}

type rawJSON struct{}

func (rawJSON) Render(w io.Writer, e entry.Entry) error {
	_, err := io.WriteString(w, e.Raw+"\n")
	return err
}

type plain struct{}

// reservedKeys are rendered positionally, not in the trailing key=val tail.
var reservedKeys = map[string]struct{}{
	"ts": {}, "time": {}, "level": {}, "msg": {}, "message": {},
}

func (plain) Render(w io.Writer, e entry.Entry) error {
	if !e.Parsed {
		_, err := io.WriteString(w, e.Raw+"\n")
		return err
	}

	var b strings.Builder
	if e.HasTS {
		b.WriteString(e.TS.UTC().Format(time.RFC3339))
		b.WriteByte(' ')
	}
	if e.Level != "" {
		b.WriteString(strings.ToUpper(e.Level))
		b.WriteByte(' ')
	}
	if e.Msg != "" {
		b.WriteString(e.Msg)
	}

	keys := make([]string, 0, len(e.Fields))
	for k := range e.Fields {
		if _, skip := reservedKeys[k]; skip {
			continue
		}
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		v, _ := e.FieldString(k)
		b.WriteByte(' ')
		b.WriteString(k)
		b.WriteByte('=')
		b.WriteString(quoteIfNeeded(v))
	}
	b.WriteByte('\n')
	_, err := io.WriteString(w, b.String())
	return err
}

func quoteIfNeeded(s string) string {
	if s == "" {
		return `""`
	}
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c == ' ' || c == '"' || c == '\\' || c == '\t' || c == '\n' {
			return fmt.Sprintf("%q", s)
		}
	}
	return s
}
