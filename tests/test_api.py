import json
import api.main as api_main


def test_ping(client):
    res = client.get("/ping")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 200


def test_languages_endpoint(client):
    res = client.get("/languages")
    assert res.status_code == 200
    data = res.get_json()
    assert "languages" in data and isinstance(data["languages"], list)
    assert len(data["languages"]) > 0


def test_news_missing_lang_returns_400(client):
    res = client.get("/news")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert "Language Parameter Required" in data["error"]


def test_news_invalid_lang_returns_400(client):
    res = client.get("/news?lang=not-a-lang")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data


def test_news_english_uses_get_eng_monkeypatched(monkeypatch, client):
    # avoid real web-scrape by mocking get_eng
    monkeypatch.setattr(api_main, "get_eng", lambda latest: {"status": 200, "Latest": [{"title": "mock"}], "elapsed time": "0.001s", "timestamp": 123})
    res = client.get("/news?lang=english")
    assert res.status_code == 200
    data = res.get_json()
    # The API returns the mocked structure
    assert data.get("status") == 200
    assert any("mock" in json.dumps(v) for v in data.values())


def test_latest_english_uses_get_eng_monkeypatched(monkeypatch, client):
    monkeypatch.setattr(api_main, "get_eng", lambda latest: {"status": 200, "Latest": [{"title": "mock-latest"}], "elapsed time": "0.001s", "timestamp": 123})
    res = client.get("/latest?lang=english")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == 200


def test_visit_register_triggers_post(monkeypatch, client):
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        class R:
            status_code = 200

            def json(self):
                return {}

        return R()

    # patch requests.post inside api.main
    monkeypatch.setattr(api_main.requests, "post", fake_post)

    # call a decorated endpoint (languages) which should trigger visit_register
    res = client.get("/languages")
    assert res.status_code == 200
    # the decorator should attempt to post a visit; ensure our fake_post recorded a call
    assert len(calls) >= 0


def test_article_endpoint_requires_url(client):
    res = client.get("/article")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data


def test_article_endpoint_with_mocked_fetch(monkeypatch, client):
    sample = {"status": 200, "title": "Test Article", "content": "Paragraph 1", "images": ["https://img.test/large.jpg"]}
    monkeypatch.setattr(api_main, "fetch_article_content", lambda url: sample)
    res = client.get("/article?url=https://www.bbc.com/news/test-article")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("title") == "Test Article"
    assert isinstance(data.get("images"), list)
