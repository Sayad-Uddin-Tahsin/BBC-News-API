import threading
import flask
from flask import Flask
from requests_html import HTMLSession
import time
import json
import logging
import pytz
from datetime import datetime
import os

open('log.txt', 'w').close()


# ================ LOGGING INITIATION ================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter("[%(levelname)s] %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_format)

file_handler = logging.FileHandler("log.txt")
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter("[%(levelname)s] %(message)s\n")
file_handler.setFormatter(file_format)


class NoFlaskFilter(logging.Filter):
  def filter(self, record):
    message = record.getMessage()
    return not ('HTTP/1.1' in message and ('GET' in message or 'OPTIONS *'))


console_handler.addFilter(NoFlaskFilter())
file_handler.addFilter(NoFlaskFilter())
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ================ FLASK INITIATION ================
app = Flask(__name__)
session = HTMLSession()

# ================ DHAKA TIME ================
def ctime():
  timezone = pytz.timezone('Asia/Dhaka')
  ctime = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S ')
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

# ---------------- DOC HTML ----------------
Info = """<!DOCTYPE html>
<html>
  <head>
    <title>BBC News API Documentation</title>
  </head>
  <body>
    <a id="urlFormation" style="font-size:20px">
      URL Formation: <span style="font-size:18px"><code>/{language}/{type}</code></span>
    </a>
    <br>
    <br>
    <a id="types" style="font-size:20px">
      <u>Types</u>
      <span style="font-size:16px">
      <li>All News: <code>/news</code></li>
      <li>Latest News: <code>/latest</code></li>
      <span>
    </a>
    <br>
    <a id="languages"style="font-size:20px">
      <u>Supported Languages</u>
    </a>
    <span style="font-size:15px">
      <li>Arabic: <code>/arabic/</code></li>
      <li>Chinese: <code>/chinese/</code></li>
      <li>Indonesian: <code>/indonesian/</code></li>
      <li>Kyrgyz: <code>/kyrgyz/</code></li>
      <li>Persian: <code>/persian/</code></li>
      <li>Somali: <code>/somali/</code></li>
      <li>Turkish: <code>/turkish/</code></li>
      <li>Vietnamese: <code>/vietnamese/</code></li>
      <li>Azeri: <code>/azeri/</code></li>
      <li>French: <code>/french/</code></li>
      <li>Japanese: <code>/japanese/</code></li>
      <li>Marathi: <code>/marathi/</code></li>
      <li>Portuguese: <code>/portuguese/</code></li>
      <li>Spanish: <code>/spanish/</code></li>
      <li>Ukrainian: <code>/ukrainian/</code></li>
      <li>Bengali: <code>/bengali/</code></li>
      <li>Hausa: <code>/hausa/</code></li>
      <li>Kinyarwanda: <code>/kinyarwanda/</code></li>
      <li>Nepali: <code>/nepali/</code></li>
      <li>Russian: <code>/russian/</code></li>
      <li>Swahili: <code>/swahili/</code></li>
      <li>Urdu: <code>/urdu/</code></li>
      <li>Burmese: <code>/burmese/</code></li>
      <li>Hindi: <code>/hindi/</code></li>
      <li>Kirundi: <code>/kirundi/</code></li>
      <li>Pashto: <code>/pashto/</code></li>
      <li>Sinhala: <code>/sinhala/</code></li>
      <li>Tamil: <code>/tamil/</code></li>
      <li>Uzbek: <code>/uzbek/</code></li>
   	</span>
  </body>
</html>"""

# ================ ENDPOINTS ================
@app.route("/")
def main():
    logger.info(f"{ctime()}: [ENDPOINT] STATUS endpoint called - 200")

    return flask.Response(
        json.dumps({"status": "OK"}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200
    )

@app.route('/doc')
@app.route('/doc/')
async def doc():
    logger.info(f"{ctime()}: [ENDPOINT] DOC endpoint called - 200")
    return Info

def _get1(lang):
    start = int(time.time())
    r = session.get(lang)
    match = r.html.find("div.bbc-1ajedpd")
    response = {}
    response['status'] = 200
    latest = True
    try:
        sections = match[0].find("section")
        sections.pop(len(sections) - 1)
        for section in sections:
            section_name = section.find("h2")
            if section_name:
                news = []
                lis = section.find("li")
                for li in lis:
                    promo_image = li.find("div.promo-image")[0].find("img")[0].attrs['src']
                    promo_text = li.find("div.promo-text")[0].find("h3")[0]
                    title = promo_text.text
                    link = list(promo_text.absolute_links)[0]
                    news.append({
                    "title": str(title),
                    "news_link": str(link),
                    "image_link": str(promo_image)
                    })
                if news:
                    response[section_name[0].text.strip()] = news
                    if latest:
                        response['latest'] = {}
                        response['latest'][section_name[0].text.strip()] = news
                        latest = False
        end = int(time.time())
        duration = end - start
        response['elapsed time'] = f"{duration:.2f}s"
        response['last update'] = int(time.time())
        response['timestamp'] = int(time.time())
    except IndexError:
        pass
    return response

def _get2(lang):
    start = int(time.time())
    r = session.get(lang)
    div = r.html.find("div", first=True)
    response = {}
    response['status'] = 200
    sections = div.find("section")
    sections.pop(len(sections) - 1)
    latest = True
    for section in sections:
        section_name = section.find("h2")
        if section_name:
            news = []
            lis = section.find("li.ebmt73l0")
            for li in lis:
                try:
                    promo_image = li.find("picture", first=True).find("source")[0].attrs['srcset'].split(", ")[-1]
                    promo_text = li.find("h3")[0]
                    title = promo_text.text
                    link = list(promo_text.absolute_links)[0]
                    news.append({
                    "title": str(title),
                    "news_link": str(link),
                    "image_link": str(promo_image)
                    })
                except IndexError:
                    continue
                except AttributeError:
                    continue
            if news:
                response[section_name[0].text.strip()] = news
                if latest:
                    response['latest'] = {}
                    response['latest'][section_name[0].text.strip()] = news
                    latest = False
    end = int(time.time())
    duration = end - start
    response['elapsed time'] = f"{duration:.2f}s"
    response['last update'] = int(time.time())
    response['timestamp'] = int(time.time())
    return response

@app.route('/', defaults={'language': None})
@app.route('/<language>/', defaults={'type': None})
@app.route('/<language>/<type>/')
async def news(language, type):
    if str(language).lower() not in urls:
        return flask.Response(json.dumps(
        {
            "status": 400,
            "error": "Invalid Language!",
            "languages":
            f"https://{(flask.request.url).split('/')[2]}/doc#languages"
        },
        ensure_ascii=False).encode('utf8'),
                            mimetype="application/json; charset=utf-8",
                            status=400)
    
    if str(type) == 'news':
        response = _get1(urls[str(language).lower()])
        if len(response.keys()) < 4:
            response = _get2(urls[str(language).lower()])
        response.pop("latest")
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return flask.Response(json.dumps(response, ensure_ascii=False).encode('utf8'),
                          mimetype="application/json; charset=utf-8",
                          status=200)
    elif str(type) == 'latest':
        response = _get1(urls[str(language).lower()])
        if len(response.keys()) < 4:
            response = _get2(urls[str(language).lower()])
        
        latest_response = {}
        for key in response:
            if key != "latest":
                latest_response[key] = response[key]
            else:
                latest_response[list(response["latest"].keys())[0]] = response[list(response["latest"].keys())[0]]
        logger.info(
            f"{ctime()}: [ENDPOINT] NEWS (language: {language}, type: {type}) endpoint called - 200"
        )
        return flask.Response(json.dumps(latest_response, ensure_ascii=False).encode('utf8'),
                            mimetype="application/json; charset=utf-8",
                            status=200)
    else:
        logger.info(
        f"{ctime()}: [ENDPOINT] NEWS (language: {language}) endpoint called - 400 (Invalid Type)"
        )
        return flask.Response(json.dumps(
        {
            'status': 400,
            'error': 'Invalid Type!',
            'types': ['news', 'latest']
        },
        ensure_ascii=False).encode('utf8'),
                            mimetype="application/json; charset=utf-8",
                            status=400)
    
@app.route('/log/', defaults={'pin': None})
@app.route('/log/<pin>')
@app.route('/logs/', defaults={'pin': None})
@app.route('/logs/<pin>')
async def log(pin):
    if pin != None and int(pin) == int(os.environ['PIN']):
        with open("log.txt", 'r', encoding="utf-8") as f:
            logs = f.read()
        logs = logs.replace('\n', '<br>')
        logger.info(f"{ctime()}: [ENDPOINT] LOG endpoint called - 200")
        return flask.Response(logs,
                            mimetype="text/html; charset=utf-8",
                            status=200)
    else:
        logger.info(
        f"{ctime()}: [ENDPOINT] LOG endpoint called - 400 (Authorization Failed)"
        )
        return flask.Response(
        json.dumps({
            'status': 400,
            'error': 'Authorization Failed'
        },
                    ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=400,
        )

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=False)