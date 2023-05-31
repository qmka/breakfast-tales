import requests

from flask import Flask, render_template, request, flash, url_for, redirect
from flask_migrate import Migrate
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from breakfast_tales.parsers import get_rss
from breakfast_tales.parsers import parse_rss
from breakfast_tales.models import db, Article, Feed
from breakfast_tales.telegram import parse_channel

# flask init
app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"

# db init

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    with app.app_context():
        db.create_all()
        update_feeds()
        feeds = Feed.query.all()

        return render_template(
            'feed.html',
            title='Breakfast Tales',
            feeds=feeds
        )



@app.route('/description/<id>', methods=['GET'])
def get_description(id):
    article = Article.get_article_by_id(id)
    result = '<p><img src="' + article.thumbnail + '" class="img-fluid d-block"></p>'
    result += f'<p>{article.description}</p>'
    result += f'<p><a target="_blank" href="{article.url}">Перейти на сайт...</a></p>'
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
    

