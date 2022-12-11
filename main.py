import time
import json
import flask
from flask import Flask
from requests_html import HTMLSession

app = Flask(__name__)
session = HTMLSession()

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


@app.route("/")
def startup():
    print(flask.request.url)
    return {'status': "OK"}


@app.route('/info')
async def info():
    return Info

@app.route('/', defaults={'language': None})
@app.route('/<language>/', defaults={'type': None})
@app.route('/<language>/<type>/')
async def head(language, type):
    if str(language).lower() in urls:
        url = urls.get(str(language).lower())
    else:
        return flask.Response(json.dumps({"status": 400, "error": "Invalid Language!", "languages": [i.lower() for i in urls]}, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=400)
    if str(type) == 'news':
        try:
            start = int(time.time())
            r = session.get(url)

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
                    news['timestamp'] = int(time.time())
                except:
                    pass
            end = int(time.time())
            duration = end - start
            news['elapsed time'] = f"{duration:.2f}s"
            return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=200)
        except:
            news = {}
            news['status'] = 500
            news['error'] = "Something went wrong in the Server!"
            news['timestamp'] = int(time.time())
            return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=500)
    elif str(type) == 'latest':
        try:
            start = int(time.time())
            r = session.get(url)

            match = r.html.find("div.e4rwlwd0")
            sections = match[0].find('section')
            news = {}
            news['status'] = 200
            news['latest'] = ''
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
                news['latest'] = data[0]
                data.pop(0)
                news[sectitle] = data

                end = int(time.time())
                duration = end - start
                news['elapsed time'] = f"{duration:.2f}s"
                return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=200)
            except:
                news = {}
                news['status'] = 500
                news['error'] = "Something went wrong in the Server!"
                news['timestamp'] = int(time.time())
                return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=500)
        except:
            news = {}
            news['status'] = 500
            news['error'] = "Something went wrong in the Server!"
            news['timestamp'] = int(time.time())
            return flask.Response(json.dumps(news, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=500)

    else:
        return flask.Response(json.dumps({'status': 400, 'error': 'Invalid Type!', 'types': ['news', 'latest']}, ensure_ascii=False).encode('utf8'), mimetype="application/json", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
