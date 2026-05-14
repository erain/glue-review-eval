package filter

import (
	"fmt"
	"strings"
	"time"
)

// ParseDuration accepts the same forms as time.ParseDuration plus a bare
// number-of-seconds. Empty string returns 0, nil.
func ParseDuration(s string) (time.Duration, error) {
	s = strings.TrimSpace(s)
	if s == "" {
		return 0, nil
	}
	if d, err := time.ParseDuration(s); err == nil {
		return d, nil
	}
	// time.ParseDuration already handles "5m", "2h30m", "1h15m30s", etc.
	// We only fall through to a clearer error.
	return 0, fmt.Errorf("invalid duration %q", s)
}
