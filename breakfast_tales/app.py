import requests

from flask import Flask, render_template, request, flash, url_for, redirect
from flask_migrate import Migrate
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from breakfast_tales.parsers import get_rss
from breakfast_tales.parsers import parse_rss
from breakfast_tales.models import db, Article, Feed, Board
from breakfast_tales.telegram import parse_channel

BOARDS = [
    {
        'title': 'Люди',
        'slug': 'people'
    }, {
        'title': 'Машины',
        'slug': 'robots'
    }
]
FEEDS = [
    {
        'url': 'https://bolknote.ru/rss/',
        'board': BOARDS[0]
    }, {
        'url': 'https://ilyabirman.ru/meanwhile/rss/',
        'board': BOARDS[0]
    }, {
        'url': 'https://rationalnumbers.ru/rss/',
        'board': BOARDS[1]
    }, {
        'url': 'https://alexandertokarev.ru/rss/',
        'board': BOARDS[0]
    }, {
        'url': 'https://worldchess.com/news/rss/',
        'board': BOARDS[1]
    }, {
        'url': 'https://vacations-on.com/rss/',
        'board': BOARDS[1]
    }
]

# flask init
app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"

# db init

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET'])
def index():
    if request.path == '/favicon.ico':
        return app.send_static_file('favicon.ico')
    
    with app.app_context():
        db.create_all()
        create_boards()
        update_feeds()

        boards = Board.query.all()
        selected_board = Board.get_first_board()

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Board.get_first_feed_for_board(selected_board.id)

        articles = Feed.get_articles_for_feed(selected_feed.id)
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            boards=boards,
            feeds=feeds,
            articles=articles
        )


@app.route('/<board_slug>', methods=['GET'])
def get_board(board_slug):
    if request.path == '/favicon.ico':
        return app.send_static_file('favicon.ico')
    
    with app.app_context():
        boards = Board.query.all()
        selected_board = Board.get_board_by_slug(board_slug)

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Board.get_first_feed_for_board(selected_board.id)

        articles = Feed.get_articles_for_feed(selected_feed.id)
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            boards=boards,
            feeds=feeds,
            articles=articles
        )


@app.route('/<board_slug>/<feed_slug>', methods=['GET'])
def get_feed(board_slug, feed_slug):
    if request.path == '/favicon.ico':
        return app.send_static_file('favicon.ico')
    
    with app.app_context():
        boards = Board.query.all()
        selected_board = Board.get_board_by_slug(board_slug)

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Feed.get_feed_by_slug(feed_slug)

        articles = Feed.get_articles_for_feed(selected_feed.id)
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            boards=boards,
            feeds=feeds,
            articles=articles
        )


@app.route('/<board_slug>/<feed_slug>/<article_slug>', methods=['GET'])
def get_article(board_slug, feed_slug, article_slug):
    article = Article.get_article_by_slug(article_slug)
    result = '<p><img src="' + article.thumbnail + '" class="img-fluid d-block"></p>'
    result += f'<p>{article.description}</p>'
    result += f'<p><a target="_blank" href="{article.url}">Перейти на сайт...</a></p>'
    return result


def update_feeds():
    for feed in FEEDS:
        raw_feed = get_rss(feed['url'])
        parse_rss(raw_feed, feed['board']['title'])


def create_boards():
    for board in BOARDS:
        Board.add_board(board['title'], board['slug'])


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
    

