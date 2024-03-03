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
import requests

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
    "uzbek": "https://bbc.com/uzbek"
}
    # "english": "https://bbc.com"

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
        # if str(language).lower() == 'english':
        #     response = get_eng(False)
        # else:
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
        # if str(language).lower() == 'english':
        #     response = get_eng(True)
        # else:
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

@app.route("/get/", defaults={"pin": None})
@app.route("/get/<pin>")
def get(pin):
    if pin != None and int(pin) == int(os.environ["PIN"]):
        url = flask.request.args.get('url')
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "atuserid={%22val%22:%229e21b0e5-c6c0-4030-bea9-a4fb1cda1754%22}; ckns_privacy=july2019; dnsDisplayed=undefined; ccpaApplies=true; signedLspa=undefined; _sp_su=true; consentUUID=5d2eaaeb-44b1-4b19-bbe1-6b8a09c3d150; ckns_explicit=2; ckns_policy=111; ckpf_ppid=f2ea68c46ea3480489bbe6ae285a3767; ccpaUUID=3640e858-f91f-4794-923b-cb2728cba2d0; optimizelyEndUserId=oeu1709139927736r0.3322733709103538; blaize_session=9a6badbc-49a3-4777-b776-7cc0674acfaa; blaize_tracking_id=a1cf112e-5150-4e36-8db1-35ce77f5b57b; ckns_mvt=2617071d-1b7e-4440-9fda-03344c790402; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIGYA2ABi644AmQQFYALDwDsYgIwiR3AJwgAvkA; _pcid=%7B%22browserId%22%3A%22lta7zuj6le34yek0%22%7D; __tbc=%7Bkpex%7DyR4t02jrk6b8dQWPLS938OZjrMtg0ZQeLMs8GbTFrEIDZTCrEaa8DnixAlsSJgqs; xbc=%7Bkpex%7D7GKrSjX8hzvt59EbA7KHl_T49kKyC2tJ_if2gPN28uc; __gads=ID=6a53c22a55484a5b:T=1709042774:RT=1709472724:S=ALNI_MZ7a6Zu2LRhQLDxpKyfqTuhBs2J6g; _chartbeat2=.1709042773941.1709472795170.110111.BiRxC5BokbRBUpG1kBMrxe2jUI-8.1; _cb_svref=external; _chartbeat4=t=DdcF9kDjQGPjtyOF1qBlvEC74M5T&E=0&x=5877&c=2.89&y=8580&w=654; atuserid=%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%229e21b0e5-c6c0-4030-bea9-a4fb1cda1754%22%2C%22options%22%3A%7B%22end%22%3A%222025-04-04T13%3A36%3A10.137Z%22%2C%22path%22%3A%22%2F%22%7D%7D; ecos.dt=1709473012974"
        })
        with open("/tmp/html.html", "w") as f:
            f.write(r.text)
        return flask.send_file("/tmp/html.html", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
