def test_article_first_image_is_ichef():
    """Integration test: fetch a real article and ensure the first image is an ichef (high-res) URL.

    Note: This is an integration-style test that performs a real HTTP fetch. It may be skipped
    in environments without network access. The test asserts that the first image returned by
    fetch_article_content is an ichef URL and not the grey-placeholder.
    """
    from api.main import fetch_article_content

    url = "https://www.bbc.com/news/articles/cze61zg7zzpo"
    res = fetch_article_content(url)
    assert res.get("status") == 200
    imgs = res.get("images", [])
    assert imgs, "No images returned for article"
    first = imgs[0]
    assert "ichef.bbci.co.uk" in first, f"Expected first image to be an ichef URL, got: {first}"
    assert "grey-placeholder" not in first, "First image is still the grey-placeholder"
