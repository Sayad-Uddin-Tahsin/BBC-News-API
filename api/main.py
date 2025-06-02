import flask
from flask import Flask
from flask import send_from_directory
from requests_html import HTMLSession
import time
import json
import logging
import pytz
from datetime import datetime
import random
import requests
import functools
import os
import dotenv

dotenv.load_dotenv()

open("/tmp/api.log", "w").close()


# ================ LOGGING INITIATION ================
logger = logging.getLogger('BBC-API')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('/tmp/api.log')
file_handler.setLevel(logging.DEBUG)  # Log all levels to the file

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Log INFO and above to the console

custom_format = '%(asctime)s - %(filename)s - %(levelname)s - %(message)s'

class ColoredFormatter(logging.Formatter):
    # Define color codes for different log levels
    LEVEL_COLORS = {
        'DEBUG': '\033[34m',    # Blue
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m'  # Red background
    }

    MESSAGE_COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    
    RESET = '\033[0m'  # Reset color

    def format(self, record):
        # Get the color for the log level and message based on the level name
        level_color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        message_color = self.MESSAGE_COLORS.get(record.levelname, self.RESET)

        # Format the message with the colors
        log_fmt = (
            f'\033[1;34m%(asctime)s\033[0m - \033[1;36m%(filename)s\033[0m - '
            f'{level_color}\033[1m%(levelname)s\033[0m - '
            f'{message_color}%(message)s{self.RESET}'
        )
        
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

formatter = logging.Formatter(custom_format)

file_handler.setFormatter(formatter)
console_handler.setFormatter(ColoredFormatter())

# Define a custom logging filter to add the filename
class NoFlaskFilter(logging.Filter):
    def __init__(self, name: str = None) -> None:
        self.name = name if name is not None else __file__
        super().__init__(name)
    
    def filter(self, record):
        record.filename = f"{self.name}"
        message = record.getMessage()
        return True and (not ("HTTP/1.1" in message and ("GET" in message or "OPTIONS *")))


console_handler.addFilter(NoFlaskFilter("ENDPOINT"))
file_handler.addFilter(NoFlaskFilter("ENDPOINT"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ================ FLASK INITIATION ================
app = Flask(__name__, static_folder="templates", static_url_path="/static")
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
            requests.post(
                f"https://web-badge-psi.vercel.app/register-visit?api_key={os.environ.get('API_KEY')}",
                headers=json.loads(os.environ.get("HEADERS")),
                json={
                    'func_name': str(func.__name__)
                }
            )
        return result[1]
    return wrapper

def _get(lang, latest):
    start = time.time()
    response = {}
    try:
        with HTMLSession() as session:
            r = session.get(lang)
            response["status"] = r.status_code
            if r.status_code == 200:
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
                            image_link = news_li.find('div.promo-image', first=True).find('img', first=True).attrs.get('src')
                            promo_div = news_li.find('div.promo-text', first=True)
                            title_tag = promo_div.find('h3 a', first=True)
                            news_title = title_tag.text
                            news_link = list(title_tag.absolute_links)[0]
                            summary_tag = promo_div.find('p', first=True)
                            news_summary = summary_tag.text if summary_tag else None
                            section_news.append({
                                "title": news_title,
                                "summary": news_summary,
                                "news_link": news_link,
                                "image_link": image_link
                            })
                    elif method_2:
                        for news_li in news_lis:
                            news_li = news_li.find('div[data-e2e="story-promo"]', first=True)
                            image_link = news_li.find('img', first=True).attrs.get('src')
                            title_tag = news_li.find('h3 a', first=True)
                            news_title = title_tag.text
                            news_link = list(title_tag.absolute_links)[0]
                            summary_tag = news_li.find('p', first=True)
                            news_summary = summary_tag.text if summary_tag else None
                            section_news.append({
                                "title": news_title,
                                "summary": news_summary,
                                "news_link": news_link,
                                "image_link": image_link
                            })
                    if section_news:
                        response[title] = section_news
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
                if 'srcset' in image.attrs and image.attrs['srcset']:
                    image_src = image.attrs['srcset'].split(',')[0].split(' ')[0]
                else:
                    image_src = image.attrs.get('src', None)
        link = div.find('a', first=True)
        news_link = link.attrs['href'] if link else None
        return heading_text, summary_text, image_src, news_link

    response = {}
    start = time.time()
    try:
        with HTMLSession() as session:
            r = session.get('https://www.bbc.com/')
            if r.status_code != 200:
                response["status"] = 503
                response["error"] = f"Failed to retrieve content. BBC website returned status code: {r.status_code}"
                return response
            divs = r.html.find('div')
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
                        sec_news.append({
                            "title": heading,
                            "summary": summary,
                            "image_link": image,
                            "news_link": f"{urls['english']}{news_link}"
                        })
                    response["Latest"] = sec_news
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
                            sec_news.append({
                                "title": heading,
                                "summary": summary,
                                "image_link": image,
                                "news_link": f"{urls['english']}{news_link}"
                            })
                        response[title_text] = sec_news
            response = {k: v for k, v in response.items() if v not in [None, []]}
    except Exception as e:
        response["status"] = 500
        response["error"] = str(e)
    end = time.time()
    response["elapsed time"] = f"{end - start:.3f}s"
    response["timestamp"] = int(time.time())
    return response


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
@visit_register
async def doc():
    lang = random.choice(list(urls.keys()))
    logger.info(f"{ctime()}: DOC endpoint called - 200")
    return (flask.request.headers, flask.render_template("documentation.html", listOfLangs="\n".join([f"<li>{key.capitalize()}: <code>{key}</code></li>" for key in sorted(urls.keys())]), type="{type}", language="{language}", lang=lang.title(), urlForNews=f"https://{(flask.request.url).split('/')[2]}/news?lang={lang}", urlForLatest=f"https://{(flask.request.url).split('/')[2]}/latest?lang={lang}", currentYear=str(datetime.now(pytz.timezone("Asia/Dhaka")).year)))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join("/".join(app.root_path.split("/")[:3]), "Assets"),
                          'favicon.ico' ,mimetype='image/vnd.microsoft.icon')

@app.route("/code")
def temp_end():
    return flask.send_from_directory("/tmp/", 'code.html')

@app.route("/", defaults={"type": None})
@app.route("/<type>")
@visit_register
async def news(type):
    if type == "favicon.ico":
        return (flask.request.headers, "None")
    
    if type not in ['latest', 'news']:
        logger.info(
            f"{ctime()}: NEWS endpoint called - 400 (Invalid Type)"
        )
        return (flask.request.headers, flask.Response(
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
        return (flask.request.headers, flask.Response(
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
        return (flask.request.headers, flask.Response(
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
        return (flask.request.headers, flask.Response(
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
        return (flask.request.headers, flask.Response(
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
    if pin != None and int(pin) == int(os.environ["PIN"]):
        with open("/tmp/api.log", "r", encoding="utf-8") as f:
            logs = f.read()
        logs = logs.replace("\n", "<br>")
        logger.info(f"{ctime()}: LOG endpoint called - 200")
        return (flask.request.headers, flask.Response(logs, mimetype="text/html; charset=utf-8", status=200))
    else:
        logger.info(
            f"{ctime()}: LOG endpoint called - 400 (Authorization Failed)"
        )
        return (flask.request.headers, flask.Response(
            json.dumps(
                {"status": 400, "error": "Authorization Failed"}, ensure_ascii=False
            ),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))

# Serve static files for index page
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('api/templates', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
