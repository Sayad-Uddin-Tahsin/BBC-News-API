import os
import api.main as api_main


def test_log_endpoint_falls_back_to_memory_buffer(client, monkeypatch):
    # ensure PIN is set
    monkeypatch.setenv("PIN", "1234")
    # simulate environment where no file is available
    monkeypatch.setattr(api_main, "log_file", None)

    # write a message into the logger (should be picked up by ring handler)
    api_main.logger.info("test-memory-log-entry")

    res = client.get("/log/1234")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "test-memory-log-entry" in text


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
