import os
import api.main as api_main


def test_log_endpoint_returns_404_when_no_file(client, monkeypatch):
    # ensure PIN is set
    monkeypatch.setenv("PIN", "1234")
    # simulate environment where no file is available
    monkeypatch.setattr(api_main, "log_file", None)

    res = client.get("/log/1234")
    assert res.status_code == 404
    data = res.get_json()
    assert data.get("error") == "Logs not available"


def test_log_endpoint_denies_wrong_pin(client, monkeypatch):
    monkeypatch.setenv("PIN", "9999")
    res = client.get("/log/1234")
    assert res.status_code == 400
    data = res.get_json()
    assert data.get("error") == "Authorization Failed"


def test_log_endpoint_reads_file_when_present(client, monkeypatch, tmp_path):
    monkeypatch.setenv("PIN", "321")
    # create a temporary log file and point module to it
    p = tmp_path / "api.log"
    p.write_text("line-from-file")
    monkeypatch.setattr(api_main, "log_file", str(p))

    res = client.get("/log/321")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "line-from-file" in text


def test_log_endpoint_returns_404_when_path_missing(client, monkeypatch):
    monkeypatch.setenv("PIN", "555")
    # point to a non-existent file path
    monkeypatch.setattr(api_main, "log_file", "/non/existent/path/api.log")

    res = client.get("/log/555")
    assert res.status_code == 404
    data = res.get_json()
    assert data.get("error") == "Logs not available"


def test_prefer_tmp_on_vercel(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    import importlib
    import api.main as m
    # reload module to pick up new env and recompute log_file
    importlib.reload(m)
    # when VERCEL is present, log_file should be somewhere under /tmp
    assert m.log_file is None or str(m.log_file).startswith('/tmp')


def test_log_dir_respects_LOG_DIR_env(monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    import importlib
    import api.main as m
    importlib.reload(m)
    assert str(m.log_file).startswith(str(tmp_path))
