# glog

`jq | grep` for JSON-line logs. One small binary, no deps.

I got tired of piping `jq` into `grep` into `awk` just to read a service log
during dev. `glog` reads JSON-line logs from stdin or a file, filters by
level, timestamp, regex, or field equality, and prints them in a form that's
easy on the eyes (or re-emits raw JSON for chaining).

## Install

```
go install github.com/erain/glog/cmd/glog@latest
```

Or build from a checkout:

```
go build ./cmd/glog
```

## Examples

Tail a service log, errors only, last 15 minutes:

```
glog --level error --since 15m -f /var/log/app.json
```

All entries for user `alice` containing the word `retry`:

```
glog --field user=alice --grep retry app.json
```

Chain through `jq` by keeping the output as JSON:

```
glog --level warn,error --out json app.json | jq '.msg'
```

Read from stdin (which is how I usually use it):

```
my-service 2>&1 | glog --level info
```

## Flags

| Flag        | What it does                                            |
| ----------- | ------------------------------------------------------- |
| `--level`   | Comma-separated allow-list. Case-insensitive.           |
| `--since`   | Keep entries no older than this duration (e.g. `15m`).  |
| `--until`   | Keep entries at least this old (e.g. `5m`).             |
| `--grep`    | Go regex matched against the raw line.                  |
| `--field`   | `key=value` exact match. Repeatable.                    |
| `-f`, `--follow` | Tail the file as it grows. Requires a file path.   |
| `--out`     | `plain` (default) or `json`.                            |

Lines that don't parse as JSON pass through `--grep` but are rejected by any
filter that needs structured data. In `plain` mode they print as-is.

## Caveats

- `--follow` doesn't handle file rotation. If the file is replaced or
  truncated, glog will stop. Use a process supervisor or re-run.
- Timestamps are read from `ts` or `time` (RFC3339 or unix seconds).
