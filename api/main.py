import flask
from flask import Flask
from requests_html import HTMLSession
import time
import json
import logging
import pytz
from datetime import datetime
import os
import random

open("/tmp/log.txt", "w").close()


# ================ LOGGING INITIATION ================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter(
    "[%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_format)

file_handler = logging.FileHandler("/tmp/log.txt")
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter("[%(levelname)s] %(message)s\n")
file_handler.setFormatter(file_format)


class NoFlaskFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        return not ("HTTP/1.1" in message and ("GET" in message or "OPTIONS *"))


console_handler.addFilter(NoFlaskFilter())
file_handler.addFilter(NoFlaskFilter())
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ================ FLASK INITIATION ================
app = Flask(__name__)
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
    "english": "https://bbc.com"
}

# ================ ENDPOINTS ================
@app.route("/")
def main():
    logger.info(f"{ctime()}: [ENDPOINT] STATUS endpoint called - 200")

    return flask.Response(
        json.dumps({"status": "OK", "url formation": f"https://{(flask.request.url).split('/')[2]}/<type>?lang=<language>", "documentation": f"https://{(flask.request.url).split('/')[2]}/doc", "repository": "https://github.com/Sayad-Uddin-Tahsin/BBC-News-API"}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200,
    )

@app.route("/ping/")
def ping():
    logger.info(f"{ctime()}: [ENDPOINT] Ping endpoint called - 200")

    return flask.Response(
        json.dumps({"status": 200}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200,
    )

@app.route("/doc")
@app.route("/doc/")
@app.route("/docs")
@app.route("/docs/")
async def doc():
    lang = random.choice(list(urls.keys()))
    logger.info(f"{ctime()}: [ENDPOINT] DOC endpoint called - 200")
    return flask.render_template("index.html", type="{type}", language="{language}", lang=lang.title(), urlForNews=f"https://{(flask.request.url).split('/')[2]}/news?lang={lang}", urlForLatest=f"https://{(flask.request.url).split('/')[2]}/latest?lang={lang}", currentYear=str(datetime.now(pytz.timezone("Asia/Dhaka")).year))


def _get1(lang, latest):
    start = int(time.time())
    r = session.get(lang)
    match = r.html.find("div.bbc-1ajedpd")
    response = {}
    response["status"] = 200
    try:
        sections = match[0].find("section")
        sections.pop(len(sections) - 1)
        for section in sections:
            section_name = section.find("h2")
            if section_name:
                news = []
                lis = section.find("li")
                for li in lis:
                    promo_image = (
                        li.find("div.promo-image")[0].find("img")[0].attrs["src"]
                    )
                    promo_text = li.find("div.promo-text")[0].find("h3")[0]
                    title = promo_text.text
                    link = list(promo_text.absolute_links)[0]
                    news.append(
                        {
                            "title": str(title),
                            "news_link": str(link),
                            "image_link": str(promo_image),
                        }
                    )
                if news:
                    response[section_name[0].text.strip()] = news
                    if latest:
                        break
        end = int(time.time())
        duration = end - start
        response["elapsed time"] = f"{duration:.2f}s"
        response["last update"] = int(time.time())
        response["timestamp"] = int(time.time())
    except IndexError:
        pass
    return response


def _get2(lang, latest):
    start = int(time.time())
    r = session.get(lang)
    div = r.html.find("div", first=True)
    response = {}
    response["status"] = 200
    sections = div.find("section")
    sections.pop(len(sections) - 1)
    for section in sections:
        section_name = section.find("h2")
        if section_name:
            news = []
            lis = section.find("li.ebmt73l0")
            for li in lis:
                try:
                    promo_image = (
                        li.find("picture", first=True)
                        .find("source")[0]
                        .attrs["srcset"]
                        .split(", ")[-1]
                    )
                    promo_text = li.find("h3")[0]
                    title = promo_text.text
                    link = list(promo_text.absolute_links)[0]
                    news.append(
                        {
                            "title": str(title),
                            "news_link": str(link),
                            "image_link": str(promo_image),
                        }
                    )
                except IndexError:
                    continue
                except AttributeError:
                    continue
            if news:
                response[section_name[0].text.strip()] = news
                if latest:
                    break
    end = int(time.time())
    duration = end - start
    response["elapsed time"] = f"{duration:.2f}s"
    response["last update"] = int(time.time())
    response["timestamp"] = int(time.time())
    return response

def get_eng(latest):
    start = int(time.time())
    r = session.get("https://bbc.com")
    print(r.html)
    matches = r.html.find("section.module")
    response = {}
    response["status"] = 200
    # logger.info(matches)
    for match in matches:
        module_content = match.find("div.module__content")
        if module_content:
            news = []
            title = match.find("h2", first=True)
            if not title:
                title = "latest"
            try:
                media_list = module_content[0].find("ul.media-list")
                media_list_items = media_list[0].find("li.media-list__item")
                for media_list_item in media_list_items:
                    newstitle = media_list_item.find("a.media__link", first=True)
                    if newstitle:
                        news.append({"title": str(newstitle.text), "link": list(newstitle.absolute_links)[0]})
                if news:
                    response[str(title.text) if type(title) != str else title] = news
                    if latest:
                        break
                top_list = module_content[0].find("div.top-list", first=True)
                if top_list:
                    top_list_news = []
                    sectitle = top_list.find("h2", first=True).text
                    items = top_list.find("li.top-list-item")
                    for item in items:
                        top_list_news.append({"title": str(item.text), "link": str(list(item.absolute_links)[0])})
                    if top_list_news:
                        response[sectitle] = top_list_news
            except IndexError:
                feature_list = module_content[0].find("li.feature")
                if feature_list:
                    for feature in feature_list:
                        fsectitle = feature.find("h2", first=True).text
                        content = feature.find("div.feature__content", first=True)
                        media_link = content.find("a.media__link", first=True)
                        if fsectitle in response:
                            response[fsectitle].append({"title": str(media_link.text), "link": str(list(media_link.absolute_links)[0])})
                        else:
                            response[fsectitle] = [{"title": str(media_link.text), "link": str(list(media_link.absolute_links)[0])}]
            except Exception as e:
                raise e
    end = int(time.time())
    duration = end - start
    response["elapsed time"] = f"{duration:.2f}s"
    response["last update"] = int(time.time())
    response["timestamp"] = int(time.time())
    logger.info(response.keys())
    return response

@app.route("/", defaults={"type": None})
@app.route("/<type>")
async def news(type):
    if type == "favicon.ico":
        return "None"
    
    if type not in ['latest', 'news']:
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS endpoint called - 400 (Invalid Type)"
        )
        return flask.Response(
            json.dumps(
                {"status": 400, "error": "Invalid Type!", "types": ["news", "latest"]},
                ensure_ascii=False,
            ).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=400,
        )
    language = flask.request.args.get('lang')
    if language is None:
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (Type: {type}) endpoint called - 400 (Language Parameter Missing)"
        )
        return flask.Response(
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
        )
    if str(language).lower() not in urls:
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (Type: {type}) endpoint called - 400 (Invalid Language)"
        )
        return flask.Response(
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
        )

    if str(type) == "news":
        if str(language).lower() == 'english':
            response = get_eng(False)
        else:
            response = _get1(urls[str(language).lower()], False)
            if len(response.keys()) < 4:
                response = _get2(urls[str(language).lower()], False)
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=200,
        )
    elif str(type) == "latest":
        if str(language).lower() == 'english':
            response = get_eng(True)
        else:
            response = _get1(urls[str(language).lower()], True)
            if len(response.keys()) < 4:
                response = _get2(urls[str(language).lower()], True)

        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=200,
        )        

@app.route("/log/", defaults={"pin": None})
@app.route("/log/<pin>")
@app.route("/logs/", defaults={"pin": None})
@app.route("/logs/<pin>")
async def log(pin):
    if pin != None and int(pin) == int(os.environ["PIN"]):
        with open("/tmp/log.txt", "r", encoding="utf-8") as f:
            logs = f.read()
        logs = logs.replace("\n", "<br>")
        logger.info(f"{ctime()}: [ENDPOINT] LOG endpoint called - 200")
        return flask.Response(logs, mimetype="text/html; charset=utf-8", status=200)
    else:
        logger.info(
            f"{ctime()}: [ENDPOINT] LOG endpoint called - 400 (Authorization Failed)"
        )
        return flask.Response(
            json.dumps(
                {"status": 400, "error": "Authorization Failed"}, ensure_ascii=False
            ),
            mimetype="application/json; charset=utf-8",
            status=400,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
