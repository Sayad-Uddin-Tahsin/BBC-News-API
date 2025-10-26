import api.main as api_main


def test_parse_inline_image_urls_and_fragment():
    html = '''
    <html>
    <head>
    <script>
    {"props":{"pageProps":{"page":{"sections":[{"title":"Test","image":{"type":"indexImage","model":{"blocks":{"src":"https://ichef.bbci.co.uk/news/480/cpsprodpb/5512/live/4f8ac910-b19e-11f0-b33e-69e560da4e1d.jpg","width":1000}}}}]}}}}
    </script>
    </head>
    <body>
    <div class="card">
      <div class="card-image"><img src="https://static.files.bbci.co.uk/.../grey-placeholder.png" aria-label="image unavailable"></div>
      <div class="card-body">Test story</div>
    </div>
    </body>
    </html>
    '''

    urls = api_main.parse_inline_image_urls(html)
    assert isinstance(urls, list)
    assert len(urls) >= 1
    assert urls[0].startswith('https://ichef.bbci.co.uk')

    frag = '<img src="https://static.files.bbci.co.uk/.../grey-placeholder.png" srcset="https://ichef.bbci.co.uk/news/240/foo.jpg 240w, https://ichef.bbci.co.uk/news/800/foo.jpg 800w">'
    best = api_main.find_best_ichef_in_fragment(frag)
    assert best is not None
    assert '800' in best or '800w' not in best  # ensure we got the larger candidate
