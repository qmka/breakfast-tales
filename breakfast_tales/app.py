import requests

from flask import Flask, render_template, request, flash, url_for, redirect
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from breakfast_tales.parsers import get_rss
from breakfast_tales.parsers import parse_rss
from breakfast_tales.db import get_feed_from_db
from breakfast_tales.db import get_articles_from_feed
from breakfast_tales.db import get_article_by_id


# flask init
app = Flask(__name__)
app.secret_key = 'SECRET_KEY'


@app.get('/')
def index():
    # update_feeds()
    id = '6056caef7a4c48679b2302282c456ca0'
    feed = get_feed_from_db(id)
    articles = get_articles_from_feed(id, 10)

    return render_template(
        'feed.html',
        title='Breakfast Tales',
        feed=feed,
        articles=articles
    )


@app.route('/description/<id>', methods=['GET'])
def get_description(id):
    article = get_article_by_id(id)
    result = '<p><img src="' + article["thumbnail"] + '" class="img-fluid d-block"></p>'
    result += f'<p>{article["description"]}</p>'
    result += f'<p><a target="_blank" href="{article["url"]}">Перейти на сайт...</a></p>'
    return result


def update_feeds():
    urls = [
        'https://bolknote.ru/rss/',
        'https://rationalnumbers.ru/rss/'
        ]
    for url in urls:
        raw_feed = get_rss(url)
        parse_rss(raw_feed)


'''
def download(url):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)
'''

def get_thumbnail(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    img_tag = soup.find('img')
    if img_tag:
        src = img_tag.get('src')
        return src
    else:
        return ''
    

