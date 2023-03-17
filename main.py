import threading
import flask
from requests_html import HTMLSession
import time
import json
import logging
import pytz
from datetime import datetime
import os


# ================ LOGGING INITIATION ================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter("[%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_format)

file_handler = logging.FileHandler(f"/tmp/log.txt")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("[%(levelname)s] %(message)s\n", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ================ FLASK INITIATION ================
app = flask.Flask(__name__)
session = HTMLSession()

# ================ VARIABLES ================
timezone = pytz.timezone('Asia/Dhaka')
ctime = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S ')

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
    <title>Info!</title>
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

# ---------------- Others ----------------
cache = {}


# ================ HELPING Functions ================
def __get(lang):
    try:
        start = int(time.time())
        r = session.get(urls[lang])

        match = r.html.find("div.e4rwlwd0")
        sections = match[0].find('section')
        news = {}
        news['status'] = 200
        news['news'] = []
        for section in sections:
            data = []
            try:
                m = section.find("li.ebmt73l0")
                sectitle = section.find("span.e1fapd9x2")[0].text
                for i in m:
                    t = i.find("h3", first=True)
                    title = t.find('a')[0].text
                    news_link = str(t.absolute_links).replace('{\'', '').replace('\'}', '')
                    try:
                        image = \
                            session.get(news_link).html.find('div.ebmt73l0', first=True).find('img',
                                                                                              first=True).attrs[
                                'src']
                        data.append({
                            "title": title,
                            "news_link": news_link,
                            "image_link": image
                        })
                    except:
                        data.append({
                            "title": title,
                            "news_link": news_link
                        })
                if data != []:
                    news['news'].append({
                        sectitle: data
                    })
                else:
                    data_tw = []
                    m = section.find("li")
                    for i in m:
                        t = i.find("h3", first=True)
                        title = t.find('h3')[0].text
                        news_link = str(t.find('h3')[0].absolute_links).replace('{\'', '').replace(
                            '\'}', '')
                        try:
                            image = \
                                session.get(news_link).html.find('div.ebmt73l0', first=True).find('img',
                                                                                                  first=True).attrs[
                                    'src']
                            data_tw.append({
                                "title": title,
                                "news_link": news_link,
                                "image_link": image
                            })
                        except:
                            data_tw.append({
                                "title": title,
                                "news_link": news_link
                            })
                        sectitle = section.find("span.e1fapd9x2")[0].text
                        news['news'].append({
                            sectitle: data_tw
                        })
                    if data_tw == []:
                        data_th = []
                        m = section.find('div')[1]
                        t = m.find("h3", first=True)
                        title = t.find('h3')[0].text
                        news_link = str(t.find('h3')[0].absolute_links).replace('{\'', '').replace(
                            '\'}', '')
                        try:
                            image = \
                                session.get(news_link).html.find('div.ebmt73l0', first=True).find('img',
                                                                                                  first=True).attrs[
                                    'src']
                            data_th.append({
                                "title": title,
                                "news_link": news_link,
                                "image_link": image
                            })
                        except:
                            data_th.append({
                                "title": title,
                                "news_link": news_link
                            })
                        sectitle = section.find("span.e1fapd9x2")[0].text
                        news['news'].append({
                            sectitle: data_th
                        })
            except:
                pass
        end = int(time.time())
        duration = end - start
        news['elapsed time'] = f"{duration:.2f}s"
        news['timestamp'] = int(time.time())
    except:
        news = {}
        news['status'] = 500
        news['error'] = "Server encountered an unexpected condition that prevented it from fulfilling the request, maybe it's not ready yet to process your request. Please try again in 5 minutes."
        news['timestamp'] = int(time.time())

    try:
        start = int(time.time())
        match = r.html.find("div.e4rwlwd0")
        sections = match[0].find('section')
        latest = {}
        latest['status'] = 200
        latest['latest'] = ''
        section = sections[0]
        data = []
        try:
            m = section.find("li.ebmt73l0")
            sectitle = section.find("span.e1fapd9x2")[0].text
            for i in m:
                t = i.find("h3", first=True)
                title = t.find('a')[0].text
                news_link = str(t.absolute_links).replace('{\'', '').replace('\'}', '')
                try:
                    image = \
                        session.get(news_link).html.find('div.ebmt73l0', first=True).find('img',
                                                                                          first=True).attrs[
                            'src']
                    data.append({
                        "title": title,
                        "news_link": news_link,
                        "image_link": image
                    })
                except:
                    data.append({
                        "title": title,
                        "news_link": news_link
                    })
            latest['latest'] = data[0]
            data.pop(0)
            latest[sectitle] = data

            end = int(time.time())
            duration = end - start
            latest['elapsed time'] = f"{duration:.2f}s"
            latest['timestamp'] = int(time.time())
        except:
            latest = {}
            latest['status'] = 500
            latest['error'] = "Server encountered an unexpected condition that prevented it from fulfilling the request, maybe it's not ready yet to process your request. Please try again in 5 minutes."
            latest['timestamp'] = int(time.time())
    except:
        latest = {}
        latest['status'] = 500
        latest['error'] = "Server encountered an unexpected condition that prevented it from fulfilling the request, maybe it's not ready yet to process your request. Please try again in 5 minutes."
        latest['timestamp'] = int(time.time())
    return news, latest


def __startupCache():
    logging.info(f"{ctime}: [STARTUP] Startup Caching Started.")
    s = int(time.time())
    for lang in urls:
        news, latest = __get(lang)
        cache[lang] = {}
        cache[lang]['news'] = news
        cache[lang]['latest'] = latest
    logging.info(f"{ctime}: [STARTUP] Startup Caching Finished! Elapsed time: {int(time.time()) - s} s")


def __startBackgroundCaching():
    t = threading.Thread(target=__startupCache)
    t.start()


def __checkExpired():
    while True:
        for lang in cache.copy():
            if (int(time.time()) - int(cache[lang]['news']['timestamp'])) > 60:
                logging.info(f"{ctime}: [CACHING] Cached {lang}")
                news, latest = __get(lang)
                cache[lang]['news'] = news
                cache[lang]['latest'] = latest


# ================ ENDPOINTS ================
@app.route("/")
def startup():
    print(flask.request.url)
    return flask.Response(
        json.dumps({"status": "OK"}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
        status=200,
    )


@app.route('/doc')
async def doc():
    return Info


@app.route('/', defaults={'language': None})
@app.route('/<language>/', defaults={'type': None})
@app.route('/<language>/<type>/')
async def news(language, type):
    if str(language).lower() not in urls:
        return flask.Response(json.dumps({"status": 400, "error": "Invalid Language!", "languages": f"{(flask.request.url).split('/')[2]}/info#languages"}, ensure_ascii=False).encode('utf8'), mimetype="application/json; charset=utf-8", status=400)
    if str(language).lower() not in cache:
        response = {}
        response["status"] = 500
        response[
            "error"] = "Server encountered an unexpected condition that prevented it from fulfilling the request, maybe it's not ready yet to process your request. Please try again in 5 minutes."
        response["timestamp"] = int(time.time())
        return flask.Response(json.dumps(response, ensure_ascii=False).encode('utf8'), mimetype="application/json; charset=utf-8", status=400)

    if str(type) == 'news':
        s = int(time.time())
        news = cache[str(language)]['news']
        news['timestamp'] = int(time.time())
        news['elapsed time'] = f"{(int(time.time()) - s):.2f}s"
        return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json; charset=utf-8", status=200)

    elif str(type) == 'latest':
        s = int(time.time())
        news = cache[str(language)]['latest']
        news['timestamp'] = int(time.time())
        news['elapsed time'] = f"{(int(time.time()) - s):.2f}s"
        return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json; charset=utf-8",
                              status=200)

    else:
        return flask.Response(json.dumps({'status': 400, 'error': 'Invalid Type!', 'types': ['news', 'latest']}, ensure_ascii=False).encode('utf8'), mimetype="application/json; charset=utf-8", status=400)


@app.route('/log/')
async def log():
    with open("/tmp/log.txt", 'r', encoding="utf-8") as f:
        logs = f.read()
    logs = logs.replace('\n', '<br>')
    return flask.Response(logs,
                          mimetype="text/html; charset=utf-8",
                          status=200)


if __name__ == "__main__":
    __startBackgroundCaching()
    t2 = threading.Thread(target=__checkExpired)
    t2.daemon = True
    t2.start()
    app.run(host="0.0.0.0", port=8080, debug=False)
