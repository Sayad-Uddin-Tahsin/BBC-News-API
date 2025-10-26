import os
import sys
import json
import pathlib
import pytest

# Ensure repo root is on sys.path so test runner can import `api` package
ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Some environments may not have requests_html fully importable during tests (it
# may try to import optional native deps). Provide a minimal stub for
# `requests_html.HTMLSession` so importing `api.main` succeeds. Tests that need
# real scraping still mock `get_eng`/_get so the stub won't be used at runtime.
try:
    import requests_html  # noqa: F401
except Exception:
    import types

    mod = types.ModuleType("requests_html")

    class FakeSession:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, *a, **k):
            # Return a minimal object with attributes used during import-time
            class R:
                status_code = 200

                def __init__(self):
                    self.html = None

            return R()

    mod.HTMLSession = FakeSession
    sys.modules["requests_html"] = mod

from api import main as api_main


@pytest.fixture(autouse=True)
def env_and_requests(monkeypatch):
    """Set minimal environment and prevent external network calls."""
    os.environ.setdefault("API_KEY", "testkey")
    os.environ.setdefault("HEADERS", json.dumps({"Authorization": "Bearer test"}))
    os.environ.setdefault("PIN", "1234")

    # Prevent the remote register-visit POST from running during tests
    class DummyResponse:
        status_code = 200

        def json(self):
            return {}

    def fake_post(*a, **k):
        return DummyResponse()

    # monkeypatch requests.post used inside api.main
    monkeypatch.setattr(api_main.requests, "post", fake_post)

    # Keep HTMLSession but avoid network by not using it in tests (we mock get_eng/_get)
    yield


@pytest.fixture()
def client():
    app = api_main.app
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
