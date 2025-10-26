import api.main as api_main


def test_safe_headers_filters():
    # create a request context with safe and unsafe headers
    headers = {
        "User-Agent": "pytest-agent/1.0",
        "X-Unused-Header": "should-be-removed",
        "Accept": "*/*",
    }
    with api_main.app.test_request_context("/", headers=headers):
        safe = api_main.safe_headers()
        # only keys in safe_header_keys should be included
        assert "User-Agent" in safe
        assert "Accept" in safe
        assert "X-Unused-Header" not in safe


def test_best_image_from_srcset():
    src = (
        "https://ichef.bbci.co.uk/ace/ws/85/img.jpg 85w, https://ichef.bbci.co.uk/ace/ws/325/img.jpg 325w,"
        " https://ichef.bbci.co.uk/ace/ws/800/img.jpg 800w"
    )
    from api.main import best_image_from_srcset

    best = best_image_from_srcset(src)
    assert best is not None
    assert best.endswith('800/img.jpg')
