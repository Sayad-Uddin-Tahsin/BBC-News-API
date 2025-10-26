import flask
from flask import Flask
from flask import send_from_directory
try:
    from requests_html import HTMLSession
    _REQUESTS_HTML_AVAILABLE = True
except Exception as _e:
    # requests_html is a required runtime dependency for this project. Fail fast
    # with a clear message so users install the required packages instead of
    # running with a partially broken runtime.
    raise ImportError(
        "Missing required dependency 'requests_html'.\n"
        "Install project requirements: `pip install -r requirements.txt`"
    ) from _e
import time
import json
import logging
import pytz
from datetime import datetime
import secrets
import requests
import functools
import os
import dotenv
import html
from logging.handlers import RotatingFileHandler  # Added for log rotation
import tempfile
from urllib.parse import urlparse
import re as _re


def _script_blocks(html_text: str):
    """Yield script block contents (non-greedy), tolerant of spaces in end tags.

    Uses a compiled regex with DOTALL/IGNORECASE so it matches variants like
    </script>, </script >, and with attributes on the opening tag.
    """
    # Accept a closing </script> tag that may include stray whitespace or attributes
    # (some HTML producers include unexpected characters). Use a word-boundary on
    # the closing tag to be tolerant but avoid greedy over-matching.
    pattern = _re.compile(r"<script\b[^>]*>(.*?)</script\b[^>]*>", _re.IGNORECASE | _re.DOTALL)
    for m in pattern.finditer(html_text):
        yield m.group(1)


def _is_ichef_url(u: str) -> bool:
    try:
        p = urlparse(u)
        host = (p.hostname or "").lower()
        return bool(p.scheme in ("http", "https") and (host == 'ichef.bbci.co.uk' or host.endswith('.ichef.bbci.co.uk')))
    except Exception:
        return False


def _is_bbc_url(u: str) -> bool:
    try:
        p = urlparse(u)
        host = (p.hostname or "").lower()
        return bool(p.scheme in ("http", "https") and (host.endswith('bbc.com') or host.endswith('bbc.co.uk')))
    except Exception:
        return False
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

# File handler (rotating)
# Create a dedicated logs directory inside the project and use a file there.
# This avoids predictable files in /tmp and gives us a controlled location.
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logs_dir = os.path.join(base_dir, 'logs')
try:
    os.makedirs(logs_dir, exist_ok=True)
    # restrict permissions on the logs directory where possible
    try:
        os.chmod(logs_dir, 0o700)
    except Exception as _e:
        logger.debug("failed to chmod logs_dir: %s", _e)
    log_file = os.path.join(logs_dir, 'api.log')
    # ensure the file exists
    open(log_file, 'a').close()
    try:
        os.chmod(log_file, 0o600)
    except Exception as _e:
        logger.debug("failed to chmod log_file: %s", _e)
except Exception as _e:
    # fallback to a file next to this module if logs directory can't be created
    logger.debug("Failed to create logs directory %s: %s", logs_dir, _e)
    fallback_file = os.path.join(os.path.dirname(__file__), 'api.log')
    try:
        open(fallback_file, 'a').close()
        log_file = fallback_file
    except Exception:
        # last resort: fall back to stdout by setting log_file to None
        log_file = None
# rotate but keep at most a few backups
if log_file:
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024, backupCount=3)
else:
    # If we could not create a file to write logs, attach a NullHandler to avoid exceptions
    from logging import NullHandler
    file_handler = NullHandler()
file_handler.setLevel(logging.DEBUG)

# Only file logging is used in production/dev container to avoid console clutter
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ================ FLASK INITIATION ================
app = Flask(__name__, static_folder="templates", static_url_path="/static")
# Create a module-level session only if requests_html is available. If not, leave it None
# and let request-time code return a clear error.
session = HTMLSession()

# ================ DHAKA TIME ================
def ctime():
    timezone = pytz.timezone("Asia/Dhaka")
    ctime = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S ")
    return ctime


# ---------------- URL Dict ----------------
urls = {
    "arabic": "https://www.bbc.com/arabic",
    "chinese": "https://www.bbc.com/zhongwen/simp",
    "indonesian": "https://www.bbc.com/indonesia",
    "kyrgyz": "https://www.bbc.com/kyrgyz",
    "persian": "https://www.bbc.com/persian",
    "somali": "https://www.bbc.com/somali",
    "turkish": "https://www.bbc.com/turkce",
    "vietnamese": "https://www.bbc.com/vietnamese",
    "azeri": "https://www.bbc.com/azeri",
    "french": "https://www.bbc.com/afrique",
    "japanese": "https://www.bbc.com/japanese",
    "marathi": "https://www.bbc.com/marathi",
    "portuguese": "https://www.bbc.com/portuguese",
    "spanish": "https://www.bbc.com/mundo",
    "ukrainian": "https://www.bbc.com/ukrainian",
    "bengali": "https://bbc.com/bengali",
    "hausa": "https://bbc.com/hausa",
    "kinyarwanda": "https://bbc.com/gahuza",
    "nepali": "https://bbc.com/nepali",
    "russian": "https://bbc.com/russian",
    "swahili": "https://bbc.com/swahili",
    "urdu": "https://www.bbc.com/urdu",
    "burmese": "https://bbc.com/burmese",
    "hindi": "https://bbc.com/hindi",
    "kirundi": "https://bbc.com/gahuza",
    "pashto": "https://bbc.com/pashto",
    "sinhala": "https://bbc.com/sinhala",
    "tamil": "https://bbc.com/tamil",
    "uzbek": "https://bbc.com/uzbek",
    "english": "https://bbc.com",
    "yoruba": "https://www.bbc.com/yoruba"
}

# ================ HELPING FUNCTIONS ================

def visit_register(func):
    pass
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        if result[0].get("isBot") != "YES" and "Shields" not in str(result[0].get("User-Agent")):
            try:
                headers = {}
                try:
                    headers = json.loads(os.environ.get("HEADERS") or "{}")
                except Exception as _e:
                    logger.debug("visit_register: failed to parse HEADERS env: %s", _e)
                requests.post(
                    f"https://web-badge-psi.vercel.app/register-visit?api_key={os.environ.get('API_KEY')}",
                    headers=headers,
                    json={
                        'func_name': str(func.__name__)
                    },
                    timeout=5,
                )
            except Exception as _e:
                # Non-fatal: log and continue; visit registration is telemetry only
                logger.debug("visit_register: telemetry post failed: %s", _e)
        return result[1]
    return wrapper


def best_image_from_srcset(srcset: str) -> str | None:
    """Parse a srcset string and return the URL with the largest width (w).

    Example srcset entry: "https://.../img.jpg 800w"
    """
    if not srcset:
        return None
    parts = [p.strip() for p in srcset.split(',') if p.strip()]
    best_url = None
    best_w = -1
    for part in parts:
        comps = part.split()
        if len(comps) == 1:
            url = comps[0]
            w = 0
        else:
            url = comps[0]
            w_str = comps[-1]
            if w_str.endswith('w'):
                try:
                    w = int(w_str[:-1])
                except Exception:
                    w = 0
            else:
                w = 0
        # skip obvious tracking or analytics endpoints
        if any(t in url for t in ("hit.xiti", "xiti", "tracking", "analytics", "pixel")):
            continue
        if w > best_w:
            best_w = w
            best_url = url
    return best_url


def extract_width_from_url(u: str) -> int:
    """Try to extract a numeric width from BBC image URLs or srcset tokens."""
    try:
        import re

        m = re.search(r"/ws/(\d+)(?:/|/c|$)", u)
        if m:
            return int(m.group(1))
        m2 = re.search(r"(\d+)w", u)
        if m2:
            return int(m2.group(1))
        # Try to catch numeric width segments that appear in paths like '/news/1536/' or '/1024/'
        m3 = re.search(r"/(\d{3,4})(?:/|\.|$)", u)
        if m3:
            return int(m3.group(1))
    except Exception:
        return 0
    return 0


def best_image_from_element(img_el) -> str | None:
    """Given a requests_html element (img) try to extract the best image URL.

    - Prefer `srcset` values and pick the largest width candidate.
    - Fall back to `src` attribute.
    - If parent contains <source> tags with srcset, evaluate them too.
    """
    try:
        # Gather candidate URLs from srcset, parent <source>, and src
        candidates = []

        # srcset on the img
        srcset = img_el.attrs.get('srcset') if hasattr(img_el, 'attrs') else None
        if srcset:
            best = best_image_from_srcset(srcset)
            if best:
                candidates.append(best)

        # check for sibling/source tags (picture > source)
        parent = getattr(img_el, 'parent', None)
        if parent:
            sources = getattr(parent, 'find', lambda *a, **k: [])('source')
            for src in sources:
                s = src.attrs.get('srcset')
                if s:
                    best = best_image_from_srcset(s)
                    if best:
                        candidates.append(best)
        else:
            # Some pages (BBC) parse into lxml elements where the requests_html
            # wrapper doesn't expose a convenient `parent` attribute. Fall back to
            # using the underlying lxml element and walk ancestors to find
            # <source> tags (picture > source) nearby.
            el = getattr(img_el, 'element', None)
            try:
                if el is not None:
                    for anc in el.iterancestors():
                        # find any <source> descendants in this ancestor
                        srcs = anc.findall('.//source')
                        for s_el in srcs:
                            s = s_el.get('srcset') or s_el.get('data-srcset')
                            if s:
                                best = best_image_from_srcset(s)
                                if best:
                                    candidates.append(best)
                        # stop early if we already found source candidates
                        if candidates:
                            break
            except Exception as _e:
                # ignore any lxml-related errors and continue with existing candidates
                logger.debug("best_image_from_element: lxml ancestor walk failed: %s", _e)

        # fallback to src
        src = img_el.attrs.get('src') if hasattr(img_el, 'attrs') else None
        if src:
            candidates.append(src)

        # filter and pick the best candidate by numeric width where possible
        filtered = [c for c in candidates if c and not any(t in c for t in ("hit.xiti", "xiti", "tracking", "analytics", "pixel"))]
        if not filtered:
            return None

        # If candidates contain size hints (ws with numbers), pick the one with largest numeric chunk.
        # prefer the candidate with the largest detected width
        best = max(filtered, key=lambda u: extract_width_from_url(u))
        # If the best candidate is still small (<300), try to look inside the img element's srcset
        best_w = extract_width_from_url(best)
        if best_w < 300:
            # try to parse original srcset tokens more aggressively
            srcset = img_el.attrs.get('srcset') if hasattr(img_el, 'attrs') else None
            if srcset:
                alt = best_image_from_srcset(srcset)
                if alt and extract_width_from_url(alt) > best_w:
                    return alt
            # check parent sources
            parent = getattr(img_el, 'parent', None)
            if parent:
                sources = getattr(parent, 'find', lambda *a, **k: [])('source')
                for src in sources:
                    s = src.attrs.get('srcset')
                    if s:
                        alt = best_image_from_srcset(s)
                        if alt and extract_width_from_url(alt) > best_w:
                            return alt
        return best
    except Exception:
        return None


def parse_inline_image_urls(page_html: str) -> list:
    """Scan <script> tags in the page HTML and extract BBC image URLs (ichef)."""
    import re, json

    urls = []
    # find all <script> blocks robustly
    for text in _script_blocks(page_html):
        text = text.strip()
        if len(text) < 200:
            continue
        # try to decode JSON objects embedded directly
        obj = None
        try:
            obj = json.loads(text)
        except Exception:
            # try to extract the first {...} block heuristically
            try:
                start = text.index('{')
                end = text.rindex('}')
                obj = json.loads(text[start:end+1])
            except Exception:
                obj = None
        if obj is None:
            # as a fallback, scan the script text for absolute URLs and validate them
            try:
                for candidate in re.findall(r"https?://[^\s\'\"]+", text):
                    # only keep ichef host images with valid file extensions
                    if _is_ichef_url(candidate) and re.search(r"\.(?:jpg|png|webp)(?:$|\?)", candidate, re.IGNORECASE):
                        urls.append(candidate)
            except Exception as _e:
                logger.debug("parse_inline_image_urls: fallback URL scan failed: %s", _e)
            continue

        # walk the object and collect ichef urls safely
        def walk(o):
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for i in o:
                    walk(i)
            elif isinstance(o, str):
                try:
                    for url in re.findall(r"https?://[^\s\'\"]+", o):
                        if _is_ichef_url(url) and re.search(r"\.(?:jpg|png|webp)(?:$|\?)", url, re.IGNORECASE):
                            urls.append(url)
                except Exception:
                    pass
        # execute the walker on the parsed object to collect any ichef image URLs
        try:
            walk(obj)
        except Exception as _e:
            logger.debug("parse_inline_image_urls: JSON walk failed: %s", _e)

    # de-duplicate while preserving order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def map_pageprops_article_images(page_html: str) -> dict:
    """Parse inline pageProps-like JSON and map article paths (or hrefs) to best ichef image URL.

    Returns a mapping: {"/news/articles/xxx": "https://ichef...jpg", ...}
    Uses heuristics: find dicts with a 'href' or 'uri' or 'id' that contain '/news' or '/audio', and an 'image' subtree
    that contains model->blocks->src or similar.
    """
    import re, json

    mapping = {}
    # asset id -> best image url
    asset_images = {}

    for text in _script_blocks(page_html):
        text = text.strip()
        if len(text) < 200:
            continue
        obj = None
        try:
            obj = json.loads(text)
        except Exception:
            try:
                start = text.index('{')
                end = text.rindex('}')
                obj = json.loads(text[start:end+1])
            except Exception:
                obj = None
        if obj is None:
            # fallback: scan for ichef URLs in the script text
            try:
                for candidate in re.findall(r"https?://[^\s\'\"]+", text):
                    if _is_ichef_url(candidate) and re.search(r"\.(?:jpg|png|webp)(?:$|\?)", candidate, re.IGNORECASE):
                        asset_images[candidate] = candidate
            except Exception as _e:
                logger.debug("map_pageprops_article_images: fallback url scan failed: %s", _e)
            continue

        # First pass: collect image assets keyed by any id-like fields in the same dict
        def collect_assets(o, parent_keys=()):
            if isinstance(o, dict):
                # look for image src in this dict
                try:
                    src = None
                    # common places
                    if 'image' in o and isinstance(o.get('image'), (dict, str)):
                        img_obj = o.get('image')
                        if isinstance(img_obj, str) and _is_ichef_url(img_obj):
                            src = img_obj
                        elif isinstance(img_obj, dict):
                            model = img_obj.get('model') or img_obj.get('data') or img_obj
                            if isinstance(model, dict):
                                blocks = model.get('blocks')
                                if isinstance(blocks, dict):
                                    for b in blocks.values():
                                        if isinstance(b, dict):
                                            s = b.get('src') or b.get('url')
                                            if isinstance(s, str) and _is_ichef_url(s):
                                                src = s
                                                break
                                if not src:
                                    s = model.get('src') or model.get('url')
                                    if isinstance(s, str) and _is_ichef_url(s):
                                        src = s
                    # also check direct keys
                    for k in ('src', 'url'):
                        v = o.get(k)
                        if isinstance(v, str) and _is_ichef_url(v):
                            src = v
                    if src:
                        # find any id-like keys in this dict to associate with
                        ids = []
                        for idk in ('id', 'assetId', 'versionId', 'urn', 'uri'):
                            v = o.get(idk)
                            if isinstance(v, str):
                                ids.append(v)
                        # also search parent keys for possible id tokens
                        for pk in parent_keys[-3:]:
                            if isinstance(pk, str) and ('id' in pk.lower() or 'asset' in pk.lower()):
                                ids.append(pk)
                        # if no ids but model has keys
                        if not ids:
                            # try to find keys that look like p0... asset codes in string fields
                            for k, v in o.items():
                                if isinstance(v, str) and re.match(r'p0[a-z0-9]{6,}', v):
                                    ids.append(v)
                        for aid in ids:
                            asset_images[aid] = src
                except Exception as _e:
                    logger.debug("map_pageprops_article_images: inner collect_assets exception: %s", _e)
                for k, v in o.items():
                    collect_assets(v, parent_keys + (k,))
            elif isinstance(o, list):
                for i in o:
                    collect_assets(i, parent_keys)

        try:
            collect_assets(obj)
        except Exception as _e:
            logger.debug("map_pageprops_article_images: collect_assets failed: %s", _e)

        # Second pass: walk again and map href/uri objects to assets when referenced
        def map_articles(o, parent_keys=()):
            if isinstance(o, dict):
                href = None
                for k in ('href', 'uri', 'link'):
                    v = o.get(k)
                    if isinstance(v, str):
                        # consider it a candidate href if it looks like a BBC article path or a BBC URL
                        try:
                            if v.startswith('http'):
                                # full URL: validate using parsed hostname
                                if _is_bbc_url(v):
                                    href = v
                                    break
                            else:
                                # treat path-like entries that contain a top-level segment
                                # like /news/, /audio/ or /articles/ as candidate article paths.
                                # Use a regex that looks for these segments as path components
                                # to avoid accidental matches in other tokens.
                                if _re.search(r"(?:^|/)(?:news|audio|articles)(?:/|$)", v):
                                    href = v
                                    break
                        except Exception as _e:
                            logger.debug("map_pageprops_article_images: href candidate check failed: %s", _e)
                # find any id-like token inside this dict that points to assets
                referenced = set()
                for k, v in o.items():
                    if isinstance(v, str):
                        if v in asset_images:
                            referenced.add(v)
                        # urn tokens
                        if 'urn:bbc' in v and v in asset_images:
                            referenced.add(v)
                        # p0XXXX tokens
                        m = re.search(r'(p0[a-z0-9]{6,})', v)
                        if m:
                            referenced.add(m.group(1))
                # if we have a href and referenced assets, map
                if href and referenced:
                    h = href
                    if h.startswith('http'):
                        try:
                            from urllib.parse import urlparse as _up
                            p = _up(h).path
                            h = p
                        except Exception as _e:
                            logger.debug("map_pageprops_article_images: urlparse failed for %s: %s", h, _e)
                    if not h.startswith('/'):
                        h = '/' + h
                    # pick best asset (largest width) among referenced
                    best_img = None
                    best_w = -1
                    for aid in referenced:
                        img = asset_images.get(aid)
                        if img:
                            w = extract_width_from_url(img)
                            if w > best_w:
                                best_w = w
                                best_img = img
                    if best_img:
                        mapping[h] = best_img
                for k, v in o.items():
                    map_articles(v, parent_keys + (k,))
            elif isinstance(o, list):
                for i in o:
                    map_articles(i, parent_keys)

        try:
            map_articles(obj)
        except Exception as _e:
            logger.debug("map_pageprops_article_images: map_articles failed: %s", _e)

    # de-duplicate while preserving order
    seen = set()
    out = []
    for u in mapping:
        if u not in seen:
            seen.add(u)
            out.append((u, mapping[u]))
    # return dict
    return {k: v for k, v in out}


def is_advertisement_link(url: str | None, title: str | None = None, summary: str | None = None) -> bool:
    """Heuristic to detect advertisement / signup / newsletter links or boilerplate promos.

    Returns True if the link or surrounding text strongly suggests a non-news promotional item.
    """
    if not url and not title and not summary:
        return True
    try:
        s = (url or "").lower()
        t = (title or "").lower()
        m = (summary or "").lower()

        # Known signup/newsletter/email domains and patterns
        ad_tokens = [
            'cloud.email.bbc.com',
            'account.bbc.com',
            'download-the-bbc-app',
            'download-the-bbc',
            'download the bbc app',
            'royalwatch_newsletter',
            'newsletter',
            'signup',
            'sign up',
            'register',
            'subscribe',
            'campaign',
            'marketing',
            'utm_source',
            'app-download',
            'download',
            'cloud.email',
            'session.bbc.com',
        ]
        for tok in ad_tokens:
            if tok in s or tok in t or tok in m:
                return True

        # Some links are actually full absolute links to non-article hosts e.g. "https://bbc.comhttps://..."
        if s.startswith('http') and ('download' in s or 'signup' in s or 'cloud.email' in s or 'account.bbc' in s):
            return True

        # Very short or generic titles frequently indicate promotional modules.
        if t and len(t) < 6 and any(k in t for k in ('download', 'sign', 'subscribe', 'register', 'app')):
            return True

        # If URL path contains '/pages/' linking to in-site pages like download pages, ignore
        if s and '/pages/' in s:
            # further check for 'download' or 'app' in the path
            if 'download' in s or 'app' in s or 'pages/download' in s:
                return True

        return False
    except Exception:
        return False


def find_best_ichef_in_fragment(fragment_html: str) -> str | None:
    """Search a fragment of HTML (string) for ichef image URLs and return the best (largest width).

    Uses the same numeric-width extraction (`extract_width_from_url`) to prefer larger candidates.
    """
    import re

    matches = re.findall(r"https?://ichef\.bbci\.co\.uk/[^\s\"']+\.(?:jpg|png|webp)", fragment_html)
    if not matches:
        # try to extract from srcset tokens like '... 240w, ... 800w'
        ss = re.findall(r"(https?://[^\s\"']+\.(?:jpg|png|webp)\s+\d+w)", fragment_html)
        candidates = []
        for token in ss:
            parts = token.split()
            if parts:
                candidates.append(parts[0])
        matches = candidates
    if not matches:
        return None
    # pick best by numeric width
    best = max(matches, key=lambda u: extract_width_from_url(u))
    return best

def _get(lang, latest):
    start = time.time()
    response = {}
    try:
        if not _REQUESTS_HTML_AVAILABLE or HTMLSession is None:
            response["status"] = 500
            response["error"] = (
                "Missing dependency: requests_html (or one of its sub-dependencies like 'parse'). "
                "Install project requirements (pip install -r requirements.txt) to enable scraping."
            )
            return response
        with HTMLSession() as session:
            r = session.get(lang, timeout=10)
            response["status"] = r.status_code
            if r.status_code == 200:
                # parse inline JSON image URLs once for fallback use
                try:
                    page_ichef_urls = parse_inline_image_urls(r.html.html)
                except Exception:
                    page_ichef_urls = []

                # derive language code from the requested base URL (reverse lookup into `urls`)
                try:
                    language = next((k for k, v in urls.items() if v.rstrip('/') == lang.rstrip('/')), None)
                except Exception:
                    language = None
                # fallback code used when building article links in responses
                lang_code = language if language else 'english'

                # build a mapping from article paths to ichef images (if available)
                try:
                    page_image_map = map_pageprops_article_images(r.html.html)
                except Exception:
                    page_image_map = {}

                sections = r.html.find('section[aria-labelledby]:not([data-testid])')
                checked, method_2 = False, False
                for section in sections:
                    title = section.find("h2", first=True).text
                    news_lis = section.find('li:not(role)')
                    news_lis = [li for li in news_lis if any(cls.startswith('bbc-') for cls in li.attrs.get('class', [])) and 'role' not in li.attrs]
                    if not checked and news_lis[0].find('div[data-e2e="story-promo"]'):
                        checked, method_2 = True, True
                    else:
                        checked = True
                    section_news = []
                    if not method_2:
                        for news_li in news_lis:
                            # find the image element and pick the best available url (largest)
                            img_el = news_li.find('div.promo-image', first=True).find('img', first=True)
                            image_link = None
                            if img_el:
                                # prefer srcset best candidate and prefer larger alternatives if available
                                image_link = best_image_from_element(img_el)
                            # fallback: if image_link is missing or placeholder, try inline JSON or fragment
                            if (not image_link) or ('grey-placeholder.png' in (image_link or '')):
                                # try within this promo fragment first
                                try:
                                    frag = news_li.html if hasattr(news_li, 'html') else None
                                    if frag:
                                        alt = find_best_ichef_in_fragment(frag)
                                        if alt:
                                            image_link = alt
                                except Exception as _e:
                                    logger.debug("_get: fragment image scan failed: %s", _e)
                                # if still missing, pick the first page-level ichef url as a last resort
                                if not image_link and page_ichef_urls:
                                    image_link = page_ichef_urls[0]
                            promo_div = news_li.find('div.promo-text', first=True)
                            title_tag = promo_div.find('h3 a', first=True)
                            news_title = title_tag.text
                            news_link = list(title_tag.absolute_links)[0]
                            summary_tag = promo_div.find('p', first=True)
                            news_summary = summary_tag.text if summary_tag else None
                            try:
                                host = flask.request.url_root.rstrip('/')
                            except Exception:
                                host = ''
                            news_content = f"{host}/article/{lang_code}?id={urlparse(news_link).path.lstrip('/')}"
                            # try mapping from inline JSON if missing
                            if (not image_link or 'grey-placeholder' in (image_link or '')) and page_image_map:
                                mapped = page_image_map.get(urlparse(news_link).path)
                                if mapped:
                                    image_link = mapped
                            section_news.append({
                                "title": news_title,
                                "summary": news_summary,
                                "news_link": news_link,
                                "image_link": image_link,
                                "news_content": news_content
                            })
                    elif method_2:
                        for news_li in news_lis:
                            news_li = news_li.find('div[data-e2e="story-promo"]', first=True)
                            img_el = news_li.find('img', first=True)
                            image_link = best_image_from_element(img_el) if img_el else None
                            if (not image_link) or ('grey-placeholder.png' in (image_link or '')):
                                try:
                                    frag = news_li.html if hasattr(news_li, 'html') else None
                                    if frag:
                                        alt = find_best_ichef_in_fragment(frag)
                                        if alt:
                                            image_link = alt
                                except Exception as _e:
                                    logger.debug("_get(method_2): fragment image scan failed: %s", _e)
                                if not image_link and page_ichef_urls:
                                    image_link = page_ichef_urls[0]
                            title_tag = news_li.find('h3 a', first=True)
                            news_title = title_tag.text
                            news_link = list(title_tag.absolute_links)[0]
                            summary_tag = news_li.find('p', first=True)
                            news_summary = summary_tag.text if summary_tag else None
                            try:
                                host = flask.request.url_root.rstrip('/')
                            except Exception:
                                host = ''
                            news_content = f"{host}/article/{lang_code}?id={urlparse(news_link).path.lstrip('/')}"
                            # try mapping from inline JSON if missing
                            if (not image_link or 'grey-placeholder' in (image_link or '')) and page_image_map:
                                mapped = page_image_map.get(urlparse(news_link).path)
                                if mapped:
                                    image_link = mapped
                            section_news.append({
                                "title": news_title,
                                "summary": news_summary,
                                "news_link": news_link,
                                "image_link": image_link,
                                "news_content": news_content
                            })
                    if section_news:
                        # filter out entries with no title and no summary and skip ads/signup/newsletter promos
                        filtered = []
                        for it in section_news:
                            if it.get('title') in [None, ''] and it.get('summary') in [None, '']:
                                continue
                            if is_advertisement_link(it.get('news_link'), it.get('title'), it.get('summary')):
                                continue
                            filtered.append(it)
                        # dedupe by news_link preserving order
                        seen_links = set()
                        deduped = []
                        for it in filtered:
                            nl = it.get('news_link')
                            if not nl:
                                continue
                            if nl in seen_links:
                                continue
                            seen_links.add(nl)
                            deduped.append(it)
                        if deduped:
                            response[title] = deduped
                    if latest:
                        break
            else:
                response['status'] = 503
                response["error"] = f"Failed to retrieve content. BBC website returned status code: {r.status_code}"
    except Exception as e:
        response["status"] = 500
        response["error"] = str(e)
    end = time.time()
    duration = end - start
    response["elapsed time"] = f"{duration:.3f}s"
    response["timestamp"] = int(time.time())
    return response

def get_eng(latest):
    def extract_info_from_div(div):
        heading = div.find('h2[data-testid="card-headline"]', first=True)
        heading_text = heading.text if heading else None
        summary = div.find('p[data-testid="card-description"]', first=True)
        summary_text = summary.text if summary else None
        images = div.find('img')
        image_src = None
        for image in images:
            if image:
                image_src = best_image_from_element(image)
                if image_src:
                    break
        # fallback: if we still have a placeholder or no image, try fragment-level or page-level JSON
        if (not image_src) or ('grey-placeholder.png' in (image_src or '')):
            try:
                frag = div.html if hasattr(div, 'html') else None
                if frag:
                    alt = find_best_ichef_in_fragment(frag)
                    if alt:
                        image_src = alt
            except Exception as _e:
                logger.debug("get_eng.extract_info_from_div: fragment scan failed: %s", _e)
            # last resort: try page-level inline JSON (if available in enclosing scope `r`)
            try:
                page_html = r.html.html if hasattr(r, 'html') and hasattr(r.html, 'html') else None
                if (not image_src) and page_html:
                    page_urls = parse_inline_image_urls(page_html)
                    if page_urls:
                        image_src = page_urls[0]
            except Exception as _e:
                logger.debug("get_eng.extract_info_from_div: inline json parse failed: %s", _e)
        link = div.find('a', first=True)
        news_link = link.attrs['href'] if link else None
        # mapping from inline pageProps if available in enclosing scope `page_image_map`
        try:
            if (not image_src or 'grey-placeholder' in (image_src or '')) and page_image_map:
                mapped = page_image_map.get(urlparse(news_link).path) if news_link else None
                if mapped:
                    image_src = mapped
        except Exception as _e:
            logger.debug("get_eng.extract_info_from_div: mapping lookup failed: %s", _e)
        return heading_text, summary_text, image_src, news_link

    response = {}
    start = time.time()
    try:
        if not _REQUESTS_HTML_AVAILABLE or HTMLSession is None:
            return {"status": 500, "error": "Missing dependency: requests_html. Install requirements to enable scraping."}
        with HTMLSession() as session:
            r = session.get('https://www.bbc.com/', timeout=10)
            if r.status_code != 200:
                response["status"] = 503
                response["error"] = f"Failed to retrieve content. BBC website returned status code: {r.status_code}"
                return response
            divs = r.html.find('div')
            # build mapping of article paths -> ichef images for this page (English)
            try:
                page_image_map = map_pageprops_article_images(r.html.html)
            except Exception:
                page_image_map = {}
            section_divs = [div for div in divs if div.attrs.get('data-testid', '').endswith('-section')]
            response["status"] = r.status_code
            for section_div in section_divs:
                title_wrapper_divs = section_div.find('div')
                titles = [title for title in title_wrapper_divs if title.attrs.get('data-testid', '').endswith('-title-wrapper')]
                if not titles:  # For the latest category
                    sec_news = []
                    cards = section_div.find('div[data-testid$="-card"]')
                    for card in cards:
                        heading, summary, image, news_link = extract_info_from_div(card)
                        full_link = f"{urls['english']}{news_link}"
                        try:
                            host = flask.request.url_root.rstrip('/')
                        except Exception:
                            host = ''
                        news_content = f"{host}/article/english?id={urlparse(full_link).path.lstrip('/')}"
                        sec_news.append({
                            "title": heading,
                            "summary": summary,
                            "image_link": image,
                            "news_link": full_link,
                            "news_content": news_content
                        })
                        # filter and dedupe
                        filtered = [it for it in sec_news if not (it.get('title') in [None, ''] and it.get('summary') in [None, ''])]
                        seen_links = set()
                        deduped = []
                        for it in filtered:
                            nl = it.get('news_link')
                            if not nl or nl in seen_links:
                                continue
                            seen_links.add(nl)
                            deduped.append(it)
                        response["Latest"] = deduped
                    if latest:
                        break
                else:
                    for title_wrapper in titles:
                        sec_news = []
                        title = title_wrapper.find('h2', first=True)
                        title_text = title.text if title else "Untitled"
                        cards = section_div.find('div[data-testid$="-card"]')
                        for card in cards:
                            heading, summary, image, news_link = extract_info_from_div(card)
                            full_link = f"{urls['english']}{news_link}"
                            try:
                                host = flask.request.url_root.rstrip('/')
                            except Exception:
                                host = ''
                            news_content = f"{host}/article/english?id={urlparse(full_link).path.lstrip('/')}"
                            sec_news.append({
                                "title": heading,
                                "summary": summary,
                                "image_link": image,
                                "news_link": full_link,
                                "news_content": news_content
                            })
                        # filter out empty promos and dedupe by news_link and skip ads/signup/newsletter promos
                        filtered = []
                        for it in sec_news:
                            if it.get('title') in [None, ''] and it.get('summary') in [None, '']:
                                continue
                            if is_advertisement_link(it.get('news_link'), it.get('title'), it.get('summary')):
                                continue
                            filtered.append(it)
                        seen_links = set()
                        deduped = []
                        for it in filtered:
                            nl = it.get('news_link')
                            if not nl or nl in seen_links:
                                continue
                            seen_links.add(nl)
                            deduped.append(it)
                        if deduped:
                            response[title_text] = deduped
            response = {k: v for k, v in response.items() if v not in [None, []]}
    except Exception as e:
        response["status"] = 500
        response["error"] = str(e)
    end = time.time()
    response["elapsed time"] = f"{end - start:.3f}s"
    response["timestamp"] = int(time.time())
    return response


def fetch_article_content(url: str) -> dict:
    """Fetch a BBC news article URL and return title, content and images list.

    Returns a dict with at minimum keys: status, title, content, images, elapsed time, timestamp
    """
    start = time.time()
    result = {}
    try:
        # verify URL
        parsed = urlparse(url)
        if not parsed.scheme.startswith('http') or 'bbc' not in (parsed.netloc or ""):
            result["status"] = 400
            result["error"] = "Invalid or unsupported URL"
            return result

        if not _REQUESTS_HTML_AVAILABLE or HTMLSession is None:
            return {"status": 500, "error": "Missing dependency: requests_html. Install requirements to enable scraping."}
        with HTMLSession() as session:
            r = session.get(url, timeout=10)
            result["status"] = r.status_code
            if r.status_code != 200:
                result["error"] = f"Failed to retrieve content. BBC website returned status code: {r.status_code}"
                return result

            # title
            title_el = r.html.find('h1', first=True)
            title = title_el.text if title_el else None

            # detect article element (we'll extract paragraphs later, after images)
            article = r.html.find('article', first=True)

            # images: prefer images inside the main article element. Try a few selectors
            images = []
            img_elements = []
            if article:
                img_elements = article.find('img')
            else:
                # try to locate the main content area
                main_el = r.html.find('main', first=True) or r.html.find('div[role="main"]', first=True)
                if main_el:
                    img_elements = main_el.find('img')
                else:
                    img_elements = r.html.find('img')

            def is_recommendation(el):
                # check ancestor classes or attributes that hint at recommendations/related/promos
                cur = el
                for _ in range(6):
                    if not cur:
                        break
                    cls = " ".join(cur.attrs.get('class', [])) if hasattr(cur, 'attrs') else ""
                    if any(k in cls.lower() for k in ("recommend", "related", "promo", "suggest", "inline-", "js-", "most-read", "most-popular", "related-content", "recommendation")):
                        return True
                    cur = getattr(cur, 'parent', None)
                return False

            for img in img_elements:
                # skip recommendation/related images based on ancestor classes
                try:
                    if is_recommendation(img):
                        continue
                except Exception as _e:
                    logger.debug("fetch_article_content: is_recommendation check failed: %s", _e)
                best = best_image_from_element(img)
                if best:
                    # skip tracking/analytics urls
                    if any(t in best for t in ("hit.xiti", "xiti", "tracking", "analytics", "pixel")):
                        continue
                    images.append(best)

            # also attempt to use og:image meta if no images found
            if not images:
                try:
                    og = r.html.find('meta[property="og:image"]', first=True)
                    if og and 'content' in og.attrs:
                        images.append(og.attrs.get('content'))
                except Exception as _e:
                    logger.debug("fetch_article_content: og:image extraction failed: %s", _e)

            # dedupe keeping order
            seen = set()
            images = [x for x in images if not (x in seen or seen.add(x))]

            # remove obvious placeholder images (e.g., BBC grey placeholder)
            try:
                images = [i for i in images if i and 'grey-placeholder' not in i]
            except Exception as _e:
                logger.debug("fetch_article_content: filtering placeholders failed: %s", _e)

            # try to map article page images from inline JSON (prefer exact match)
            try:
                page_image_map = map_pageprops_article_images(r.html.html)
            except Exception:
                page_image_map = {}
            try:
                parsed_path = parsed.path
                mapped = page_image_map.get(parsed_path)
                if mapped and (not images or 'grey-placeholder' in images[0] or extract_width_from_url(mapped) > (extract_width_from_url(images[0]) if images else 0)):
                        # If the mapped image already exists later in the list, move it to the front
                        try:
                            if mapped in images:
                                images.remove(mapped)
                        except Exception as _e:
                            logger.debug("fetch_article_content: removing mapped duplicate failed: %s", _e)
                        images.insert(0, mapped)
            except Exception as _e:
                logger.debug("fetch_article_content: mapping lookup failed: %s", _e)

            # also try page-level fragment srcset scan as a fallback
            try:
                frag_alt = find_best_ichef_in_fragment(r.html.html)
                if frag_alt and (not images or extract_width_from_url(frag_alt) > extract_width_from_url(images[0])):
                    # ensure frag_alt is placed first; if present later, move it to the front
                    try:
                        if frag_alt in images:
                            images.remove(frag_alt)
                    except Exception as _e:
                        logger.debug("fetch_article_content: removing frag_alt duplicate failed: %s", _e)
                    images.insert(0, frag_alt)
            except Exception as _e:
                logger.debug("fetch_article_content: fragment scan failed: %s", _e)

            # Now extract textual content in-order: prefer p and headings but skip recommendation nodes
            def is_recommendation(el):
                # check ancestor classes or attributes that hint at recommendations/related/promos
                cur = el
                for _ in range(6):
                    if not cur:
                        break
                    cls = " ".join(cur.attrs.get('class', [])) if hasattr(cur, 'attrs') else ""
                    if any(k in cls.lower() for k in ("recommend", "related", "promo", "suggest", "inline-", "js-", "most-read", "most-popular", "related-content", "recommendation", "recommendations")):
                        return True
                    # check common attributes/ids
                    try:
                        for a_k, a_v in (cur.attrs.items() if hasattr(cur, 'attrs') else []):
                            if not a_v:
                                continue
                            av = str(a_v).lower()
                            if any(k in av for k in ("recommend", "related", "promo", "most-read", "most-popular", "end-of", "skip")):
                                return True
                    except Exception as _e:
                        logger.debug("is_recommendation attr scan failed: %s", _e)
                    try:
                        eid = cur.attrs.get('id', '') if hasattr(cur, 'attrs') else ''
                        if eid and any(k in eid.lower() for k in ("recommend", "related", "promo", "end-of", "most-read")):
                            return True
                    except Exception as _e:
                        logger.debug("is_recommendation id scan failed: %s", _e)
                    cur = getattr(cur, 'parent', None)
                return False

            content_nodes = []
            if article:
                content_nodes = article.find('p, h1, h2, h3, h4')
                # include BBC's data-component text blocks which sometimes contain article paragraphs
                try:
                    extra = article.find('div[data-component="text-block"]')
                    if extra:
                        # append in-document order
                        content_nodes = list(content_nodes) + list(extra)
                except Exception as _e:
                    logger.debug("fetch_article_content: extra text-block extraction failed: %s", _e)
            else:
                main_el = r.html.find('main', first=True) or r.html.find('div[role="main"]', first=True)
                if main_el:
                    content_nodes = main_el.find('p, h1, h2, h3, h4')
                    try:
                        extra = main_el.find('div[data-component="text-block"]')
                        if extra:
                            content_nodes = list(content_nodes) + list(extra)
                    except Exception as _e:
                        logger.debug("fetch_article_content: main extra text-block extraction failed: %s", _e)
                else:
                    content_nodes = r.html.find('p, h1, h2, h3, h4')

            content_paras = []
            for node in content_nodes:
                try:
                    if is_recommendation(node):
                        continue
                except Exception as _e:
                    logger.debug("fetch_article_content: is_recommendation check for node failed: %s", _e)
                text = getattr(node, 'text', None)
                if not text:
                    continue
                tstr = text.strip()
                if len(tstr) < 6 and any(k in tstr.lower() for k in ('skip', 'end')):
                    continue
                content_paras.append(tstr)

            # remove final copyright/boilerplate lines (language-agnostic)
            import re

            def is_copyright_line(s: str) -> bool:
                s2 = s.strip()
                if not s2:
                    return False
                if re.search(r'©|\bcopyright\b|\ball rights\b|\bbbc\b|\bবিবিসি\b', s2, flags=re.I | re.U):
                    return True
                if len(s2) < 200 and re.search(r'\b(bbc)\b', s2, flags=re.I):
                    return True
                return False

            while content_paras and is_copyright_line(content_paras[-1]):
                content_paras.pop()

            content = "\n\n".join(content_paras)

            result.update({
                "title": title,
                "content": content,
                "images": images,
            })
    except Exception as e:
        result["status"] = 500
        result["error"] = str(e)
    end = time.time()
    result["elapsed time"] = f"{end - start:.3f}s"
    result["timestamp"] = int(time.time())
    return result


# ================ ENDPOINTS ================

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/ping")
async def ping():
    logger.info(f"{ctime()}: Ping endpoint called - 200")

    return flask.Response(
        json.dumps({"status": 200}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200,
    )

@app.route("/doc")
@app.route("/doc/")
@app.route("/docs")
@app.route("/docs/")
@app.route("/documentation")
@app.route("/documentation/")
async def doc():
    lang = secrets.choice(list(urls.keys()))
    logger.info(f"{ctime()}: DOC endpoint called - 200")
    return flask.render_template("documentation.html", listOfLangs="\n".join([f"<li>{key.capitalize()}: <code>{key}</code></li>" for key in sorted(urls.keys())]), type="{type}", language="{language}", lang=lang.title(), urlForNews=f"https://{(flask.request.url).split('/')[2]}/news?lang={lang}", urlForLatest=f"https://{(flask.request.url).split('/')[2]}/latest?lang={lang}", currentYear=str(datetime.now(pytz.timezone("Asia/Dhaka")).year))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype='image/vnd.microsoft.icon')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml", mimetype='application/xml')


@app.route("/", defaults={"type": None})
@app.route("/<type>")
@visit_register
async def news(type):
    if type == "favicon.ico":
        return (safe_headers(), "None")
    
    if type not in ['latest', 'news']:
        logger.info(
            f"{ctime()}: NEWS endpoint called - 400 (Invalid Type)"
        )
        return (safe_headers(), flask.Response(
            json.dumps(
                {"status": 400, "error": "Invalid Type!", "types": ["news", "latest"]},
                ensure_ascii=False,
            ).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))
    language = flask.request.args.get('lang')

    if language is None:
        logger.info(
            f"{ctime()}: NEWS (Type: {type}) endpoint called - 400 (Language Parameter Missing)"
        )
        return (safe_headers(), flask.Response(
            json.dumps(
                {
                    "status": 400,
                    "error": "Language Parameter Required!",
                    "example url": f"https://{(flask.request.url).split('/')[2]}/{type}?lang=<language>",
                    "supported languages": f"https://{(flask.request.url).split('/')[2]}/doc#languages"
                },
                ensure_ascii=False,
            ).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))
    if str(language).lower() not in urls:
        logger.info(
            f"{ctime()}: NEWS (Type: {type}) endpoint called - 400 (Invalid Language)"
        )
        return (safe_headers(), flask.Response(
            json.dumps(
                {
                    "status": 400,
                    "error": "Invalid Language!",
                    "supported languages": f"https://{(flask.request.url).split('/')[2]}/doc#languages",
                },
                ensure_ascii=False,
            ).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))

    if str(type) == "news":
        if str(language).lower() == 'english':
            response = get_eng(False)
        else:
            response = _get(urls[str(language).lower()], False)
        logger.info(
            f"{ctime()}: NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return (safe_headers(), flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=response['status'],
        ))
    elif str(type) == "latest":
        if str(language).lower() == 'english':
            response = get_eng(True)
        else:
            response = _get(urls[str(language).lower()], True)

        logger.info(
            f"{ctime()}: NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return (safe_headers(), flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=response['status'],
        ))

@app.route("/log/", defaults={"pin": None})
@app.route("/log/<pin>")
@app.route("/logs/", defaults={"pin": None})
@app.route("/logs/<pin>")
@visit_register
async def log(pin):
    if pin is not None and int(pin) == int(os.environ.get("PIN", "0")):
        # prefer to expose the log file managed by this process; fall back to module-local api.log
        log_path = globals().get('log_file') or os.path.join(os.path.dirname(__file__), 'api.log')
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.read()
        except Exception as _e:
            logger.debug("log endpoint: failed to read log file %s: %s", log_path, _e)
            logs = ""
        logs = html.escape(logs).replace("\n", "<br>")
        logger.info(f"{ctime()}: LOG endpoint called - 200")
        return (safe_headers(), flask.Response(logs, mimetype="text/html; charset=utf-8", status=200))
    else:
        logger.info(f"{ctime()}: LOG endpoint called - 400 (Authorization Failed)")
        return (safe_headers(), flask.Response(
            json.dumps({"status": 400, "error": "Authorization Failed"}, ensure_ascii=False),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))

# Serve static files for index page
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)
                                

@app.route("/languages")
@visit_register
async def languages():
    response = {
        "status": 200,
        "languages": [
            {
                "code": code,
                "name": code.capitalize(),
                "url": url,
                "description": f"BBC News in {code.capitalize()}"
            }
            for code, url in urls.items()
        ]
    }
    return (safe_headers(), flask.Response(
        json.dumps(response, ensure_ascii=False).encode("utf8"),
        mimetype="application/json; charset=utf-8",
        status=200,
    ))

                            

@app.route("/article")
async def article():
    """Fetch a single BBC news article and return title, content and images.

    Query params:
    - url: full article URL (must be a bbc domain)
    """
    url = flask.request.args.get('url')
    # alternatively accept lang + path (e.g. ?lang=english&path=/news/articles/xxxxx)
    if not url:
        lang = flask.request.args.get('lang')
        path = flask.request.args.get('path') or flask.request.args.get('id')
        if lang and path:
            if str(lang).lower() not in urls:
                resp = flask.Response(
                    json.dumps({"status": 400, "error": "Invalid language for article endpoint"}, ensure_ascii=False).encode('utf8'),
                    mimetype="application/json; charset=utf-8",
                    status=400,
                )
                try:
                    resp.headers.update(safe_headers())
                except Exception as _e:
                    logger.debug("article: failed to update headers (invalid language): %s", _e)
                return resp
            base = urls[str(lang).lower()]
            # ensure path begins with '/'
            if not path.startswith('/'):
                path = '/' + path
            url = base.rstrip('/') + path
        else:
            resp = flask.Response(
                json.dumps({"status": 400, "error": "Article URL required: ?url=<full_article_url> or ?lang=<language>&path=<path>"}, ensure_ascii=False).encode('utf8'),
                mimetype="application/json; charset=utf-8",
                status=400,
            )
            try:
                resp.headers.update(safe_headers())
            except Exception as _e:
                logger.debug("article: failed to update headers (missing url/lang): %s", _e)
            return resp
        try:
            resp.headers.update(safe_headers())
        except Exception as _e:
            logger.debug("article: failed to update headers: %s", _e)
        return resp

    # basic validation
    parsed = urlparse(url)
    if not parsed.scheme.startswith('http') or 'bbc' not in (parsed.netloc or ""):
        resp = flask.Response(
            json.dumps({"status": 400, "error": "Invalid or unsupported URL"}, ensure_ascii=False).encode('utf8'),
            mimetype="application/json; charset=utf-8",
            status=400,
        )
        try:
            resp.headers.update(safe_headers())
        except Exception as _e:
            logger.debug("article: failed to update headers: %s", _e)
        return resp

    response = fetch_article_content(url)
    status_code = response.get('status', 500)
    resp = flask.Response(
        json.dumps(response, ensure_ascii=False).encode('utf8'),
        mimetype="application/json; charset=utf-8",
        status=status_code,
    )
    # attach safe headers
    try:
        resp.headers.update(safe_headers())
    except Exception as _e:
        # if safe_headers fails (no request context), log and continue
        logger.debug("article: failed to attach safe headers: %s", _e)
    return resp


@app.route("/article/<language>")
async def article_by_language(language):
    """Alternate article endpoint: /article/{language}?id={path}

    Example: /article/english?id=news/articles/cx2n7k2veywo
    """
    # normalize language
    if str(language).lower() not in urls:
        resp = flask.Response(
            json.dumps({"status": 400, "error": "Invalid language for article endpoint"}, ensure_ascii=False).encode('utf8'),
            mimetype="application/json; charset=utf-8",
            status=400,
        )
        try:
            resp.headers.update(safe_headers())
        except Exception as _e:
            logger.debug("article_by_language: failed to update headers: %s", _e)
        return resp

    ident = flask.request.args.get('id') or flask.request.args.get('path') or flask.request.args.get('article')
    if not ident:
        resp = flask.Response(
            json.dumps({"status": 400, "error": "Article id required: ?id=<path>"}, ensure_ascii=False).encode('utf8'),
            mimetype="application/json; charset=utf-8",
            status=400,
        )
        try:
            resp.headers.update(safe_headers())
        except Exception as _e:
            logger.debug("article_by_language: failed to update headers (missing id): %s", _e)
        return resp

    # ensure path starts with '/'
    if not ident.startswith('/'):
        ident = '/' + ident
    base = urls[str(language).lower()]
    url = base.rstrip('/') + ident
    response = fetch_article_content(url)
    status_code = response.get('status', 500)
    resp = flask.Response(
        json.dumps(response, ensure_ascii=False).encode('utf8'),
        mimetype="application/json; charset=utf-8",
        status=status_code,
    )
    try:
        resp.headers.update(safe_headers())
    except Exception as _e:
        logger.debug("article_by_language: failed to update headers: %s", _e)
    return resp

# Add this function after the visit_register decorator
def safe_headers():
    """Return a sanitized version of request headers with only safe headers."""
    safe_header_keys = {
        'User-Agent',
        'Accept',
        'Accept-Language',
        'Accept-Encoding',
        'Connection',
        'Host'
    }
    return {html.escape(k): html.escape(v) for k, v in flask.request.headers.items() if k in safe_header_keys}

if __name__ == "__main__":
    # For local development the host and debug can be configured via env vars.
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '8080'))
    debug_env = str(os.environ.get('FLASK_DEBUG', 'False')).lower() in ('1', 'true', 'yes')
    app.run(host=host, port=port, debug=debug_env)
