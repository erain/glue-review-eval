def test_healthz_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_healthz_no_auth_required(client):
    # No X-API-Key header; still 200.
    r = client.get("/healthz")
    assert r.status_code == 200


def test_healthz_ignores_bad_key(client):
    r = client.get("/healthz", headers={"X-API-Key": "wrong"})
    assert r.status_code == 200
