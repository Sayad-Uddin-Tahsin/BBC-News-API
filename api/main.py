import flask
from flask import Flask
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

# ================ HELPING FUNCTIONS ================

def visit_register(func):
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
                    try:
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
                    except IndexError:
                        pass
        end = int(time.time())
        duration = end - start
        response["elapsed time"] = f"{duration:.2f}s"
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
    response["timestamp"] = int(time.time())
    return response

def get_eng(latest):
    start = int(time.time())
    r = session.get("https://bbc.com")
    response = {}
    article = r.html.find("article", first=True)
    section = article.find("section", first=True)
    code = section.find("div", first=True).find("div", first=True).find("div", first=True).attrs['class'][0]
    d = r.html.find(f"div.{code}")
    d = [i for i in d if i is not None]
    response = {}
    response["status"] = 200
    for i in d:
        title_wrapper = i.find("div.sc-8a80f6eb-1", first=True)
        if title_wrapper:
            th2 = title_wrapper.find("h2", first=True)
            if th2:
                sectitle = th2.text
        else:
            sectitle = "latest"
        
        newsWrappers = i.find("div.sc-4befc967-0")
        for wrapper in newsWrappers:
            link_wrapper = wrapper.find("a.sc-4befc967-1", first=True)
            link = list(link_wrapper.absolute_links)[0]
            newsDiv = wrapper.find(f"div.{code}")
            text_wrapper = wrapper.find("div.sc-4fedabc7-0", first=True)
            if text_wrapper != None:
                newstitle = text_wrapper.find("h2", first=True).text
            description_wrapper = wrapper.find("p.sc-b8778340-4", first=True)
            if description_wrapper != None:
                newsdescription = description_wrapper.text
            
            dict_wrapped = {
                "title": newstitle,
                "news_description": newsdescription,
                "news_link": link
            }
            if sectitle in response:
                response[sectitle].append(dict_wrapped)
            else:
                response[sectitle] = [dict_wrapped]
        if latest:
            break
    end = int(time.time())
    duration = end - start
    response["elapsed time"] = f"{duration:.2f}s"
    response["timestamp"] = int(time.time())
    return response


# ================ ENDPOINTS ================

@app.route("/")
@visit_register
async def main():
    logger.info(f"{ctime()}: [ENDPOINT] STATUS endpoint called - 200")

    return (flask.request.headers, flask.Response(
        json.dumps({"status": "OK", "url formation": f"https://{(flask.request.url).split('/')[2]}/<type>?lang=<language>", "documentation": f"https://{(flask.request.url).split('/')[2]}/documentation", "get in touch": f"https://{(flask.request.url).split('/')[2]}/documentation#get-in-touch", "repository": "https://github.com/Sayad-Uddin-Tahsin/BBC-News-API"}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200,
    ))

@app.route("/ping/")
async def ping():
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
@app.route("/documentation")
@app.route("/documentation/")
@visit_register
async def doc():
    lang = random.choice(list(urls.keys()))
    logger.info(f"{ctime()}: [ENDPOINT] DOC endpoint called - 200")
    return (flask.request.headers, flask.render_template("index.html", type="{type}", language="{language}", lang=lang.title(), urlForNews=f"https://{(flask.request.url).split('/')[2]}/news?lang={lang}", urlForLatest=f"https://{(flask.request.url).split('/')[2]}/latest?lang={lang}", currentYear=str(datetime.now(pytz.timezone("Asia/Dhaka")).year)))


@app.route("/", defaults={"type": None})
@app.route("/<type>")
@visit_register
async def news(type):
    if type == "favicon.ico":
        return (flask.request.headers, "None")
    
    if type not in ['latest', 'news']:
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS endpoint called - 400 (Invalid Type)"
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
            f"{ctime()}: [ENDPOINT] NEWS (Type: {type}) endpoint called - 400 (Language Parameter Missing)"
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
            f"{ctime()}: [ENDPOINT] NEWS (Type: {type}) endpoint called - 400 (Invalid Language)"
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
            response = _get1(urls[str(language).lower()], False)
            if len(response.keys()) < 4:
                response = _get2(urls[str(language).lower()], False)
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return (flask.request.headers, flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=200,
        ))
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
        return (flask.request.headers, flask.Response(
            json.dumps(response, ensure_ascii=False).encode("utf8"),
            mimetype="application/json; charset=utf-8",
            status=200,
        ))

@app.route("/log/", defaults={"pin": None})
@app.route("/log/<pin>")
@app.route("/logs/", defaults={"pin": None})
@app.route("/logs/<pin>")
@visit_register
async def log(pin):
    if pin != None and int(pin) == int(9840):
        with open("/tmp/log.txt", "r", encoding="utf-8") as f:
            logs = f.read()
        logs = logs.replace("\n", "<br>")
        logger.info(f"{ctime()}: [ENDPOINT] LOG endpoint called - 200")
        return (flask.request.headers, flask.Response(logs, mimetype="text/html; charset=utf-8", status=200))
    else:
        logger.info(
            f"{ctime()}: [ENDPOINT] LOG endpoint called - 400 (Authorization Failed)"
        )
        return (flask.request.headers, flask.Response(
            json.dumps(
                {"status": 400, "error": "Authorization Failed"}, ensure_ascii=False
            ),
            mimetype="application/json; charset=utf-8",
            status=400,
        ))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
