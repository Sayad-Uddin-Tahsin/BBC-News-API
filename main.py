import flask
from flask import *
from requests_html import HTMLSession
import time
import json
import logging

app = Flask(__name__)

@app.route("/")
def main():
  print(flask.request.url)
  return {'status': "OK"}

@app.route("/news/")
def head():
  try:
    session = HTMLSession()
    r = session.get("https://bbc.com/bengali")
    
    match = r.html.find("div.e4rwlwd0")
    sections = match[0].find('section')
    news = {}
    news['status'] = 200
    news['news'] = []
    for section in sections:
      data = []
      m = section.find("li")
      sectitle = section.find("span.e1fapd9x2")[0].text
      if sectitle != "অডিও ও ভিডিও":
        for i in m:
          t = i.find("h3", first=True)
          title = t.find('h3')[0].text
          news_link = str(t.absolute_links).replace('{\'', '').replace('\'}', '')
          try:
            image = session.get(news_link).html.find('div.ebmt73l0', first=True).find('img', first=True).attrs['src']
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
      else:
        for i in range(len(m) - 2):
          i = m[i]
          t = i.find("h3", first=True)
          title = t.find('h3')[0].text
          news_link = str(t.absolute_links).replace('{\'', '').replace('\'}', '')
          try:
            image = session.get(news_link).html.find('div.ebmt73l0', first=True).find('img', first=True).attrs[
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
          news_link = str(t.find('h3')[0].absolute_links).replace('{\'', '').replace('\'}', '')
          try:
            image = session.get(news_link).html.find('div.ebmt73l0', first=True).find('img', first=True).attrs['src']
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
          news_link = str(t.find('h3')[0].absolute_links).replace('{\'', '').replace('\'}', '')
          try:
            image = session.get(news_link).html.find('div.ebmt73l0', first=True).find('img', first=True).attrs[
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
    return json.dumps(news, ensure_ascii=False)
  except:
    news = {}
    news['status'] = 500
    news['news'] = []
    news['timestamp'] = int(time.time())
    return json.dumps(news, ensure_ascii=False)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=False)
