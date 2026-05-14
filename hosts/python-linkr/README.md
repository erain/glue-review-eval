# linkr

A tiny URL shortener I built because every paid service wants $9/month for what
is essentially a hash table. FastAPI in front, SQLite + SQLAlchemy in back,
six-character base62 short IDs.

It is intentionally small. Read the source in an afternoon.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export LINKR_API_KEY=$(openssl rand -hex 16)
uvicorn app.main:create_app --factory --reload
```

The app writes to `./linkr.db` by default. Override with `LINKR_DB_URL`
(any SQLAlchemy URL works, though I have only really tried SQLite).

## API key

Writes are gated by an `X-API-Key` header that has to match `LINKR_API_KEY`.
If the env var is unset the auth dependency returns `503 not configured`,
which is a deliberate fail-loud signal that you forgot to configure the app
rather than a silent open-to-the-world default.

Reads of the public redirect (`GET /{short_id}`) and `GET /healthz` do not
require a key.

## Endpoints

```text
POST   /links              create a short link        (auth)
GET    /links/{short_id}   metadata + hit count       (auth)
DELETE /links/{short_id}   soft-delete                (auth)
GET    /{short_id}         302 redirect, ++hits
GET    /healthz            liveness
```

## Examples

```bash
curl -sX POST http://localhost:8000/links \
  -H "X-API-Key: $LINKR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://anthropic.com"}'
# => {"short_id":"aB3xQ1","url":"https://anthropic.com"}

curl -sI http://localhost:8000/aB3xQ1
# => HTTP/1.1 302 Found
#    location: https://anthropic.com
```

## Tests

```bash
pytest -q
```

In-memory SQLite, no network. Should finish in well under a second.
