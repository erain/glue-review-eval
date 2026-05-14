// Command glog filters and pretty-prints JSON-line logs.
package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/erain/glog/entry"
	"github.com/erain/glog/filter"
	"github.com/erain/glog/render"
	"github.com/erain/glog/tail"
)

const usage = `glog - filter and pretty-print JSON-line logs

Usage:
  glog [flags] [file]

Flags:
  --level   comma-separated allow-list of level values (case-insensitive)
  --since   keep entries no older than this duration, e.g. 1h
  --until   keep entries at least this old, e.g. 5m
  --grep    Go regex matched against the raw line
  --field   key=value exact match; repeatable
  -f, --follow   tail the file as it grows
  --out     plain|json (default plain)
`

// repeatable collects --field flag values. It satisfies flag.Value.
type repeatable []string

func (r *repeatable) String() string     { return fmt.Sprint([]string(*r)) }
func (r *repeatable) Set(v string) error { *r = append(*r, v); return nil }

type options struct {
	level  string
	since  string
	until  string
	grep   string
	fields repeatable
	follow bool
	out    string
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}

func run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	var opt options
	fs := flag.NewFlagSet("glog", flag.ContinueOnError)
	fs.SetOutput(stderr)
	fs.Usage = func() { fmt.Fprint(stderr, usage) }

	fs.StringVar(&opt.level, "level", "", "")
	fs.StringVar(&opt.since, "since", "", "")
	fs.StringVar(&opt.until, "until", "", "")
	fs.StringVar(&opt.grep, "grep", "", "")
	fs.Var(&opt.fields, "field", "")
	fs.BoolVar(&opt.follow, "follow", false, "")
	fs.BoolVar(&opt.follow, "f", false, "")
	fs.StringVar(&opt.out, "out", "plain", "")

	if err := fs.Parse(args); err != nil {
		return 2
	}

	since, err := filter.ParseDuration(opt.since)
	if err != nil {
		fmt.Fprintln(stderr, "glog:", err)
		return 2
	}
	until, err := filter.ParseDuration(opt.until)
	if err != nil {
		fmt.Fprintln(stderr, "glog:", err)
		return 2
	}

	flt, err := filter.New(opt.level, opt.grep, opt.fields, since, until, time.Now())
	if err != nil {
		fmt.Fprintln(stderr, "glog:", err)
		return 2
	}

	r, err := render.New(opt.out)
	if err != nil {
		fmt.Fprintln(stderr, "glog:", err)
		return 2
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()

	var path string
	if a := fs.Args(); len(a) == 1 && a[0] != "-" {
		path = a[0]
	} else if len(a) > 1 {
		fmt.Fprintln(stderr, "glog: at most one file argument")
		return 2
	}

	if opt.follow && path == "" {
		fmt.Fprintln(stderr, "glog: --follow requires a file")
		return 2
	}

	lines, cleanup, err := openSource(ctx, path, opt.follow, stdin)
	if err != nil {
		fmt.Fprintln(stderr, "glog:", err)
		return 1
	}
	defer cleanup()

	for line := range lines {
		e := entry.Parse(line)
		if !flt.Match(e) {
			continue
		}
		if err := r.Render(stdout, e); err != nil {
			fmt.Fprintln(stderr, "glog:", err)
			return 1
		}
	}
	return 0
}

func openSource(ctx context.Context, path string, follow bool, stdin io.Reader) (<-chan string, func(), error) {
	noop := func() {}
	if follow {
		ch, err := tail.Follow(ctx, path)
		return ch, noop, err
	}
	if path == "" {
		return tail.Lines(ctx, stdin), noop, nil
	}
	f, err := os.Open(path)
	if err != nil {
		return nil, noop, err
	}
	return tail.Lines(ctx, f), func() { f.Close() }, nil
}
