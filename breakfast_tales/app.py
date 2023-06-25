# import requests
import yaml

from flask import Flask, render_template, request, flash, url_for, redirect
from flask_migrate import Migrate
from functools import wraps
from bs4 import BeautifulSoup

from breakfast_tales.parsers import get_rss
from breakfast_tales.parsers import parse_rss, parse_tj, parse_telegram, parse_kanobu
from breakfast_tales.models import db, Article, Feed, Board


# flask init
app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"

# db init
db.init_app(app)
migrate = Migrate(app, db)


def favicon_route(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.path == '/favicon.ico':
            return app.send_static_file('favicon.ico')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
@favicon_route
def index():
    with app.app_context():
        db.create_all()
        boards = Board.query.all()
        selected_board = Board.get_first_board()

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Board.get_first_feed_for_board(selected_board.id)

        articles = Feed.get_articles_for_feed(selected_feed.id, limit=30)
        is_article_selected = False
        selected_article = None
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            selected_article=selected_article,
            boards=boards,
            feeds=feeds,
            articles=articles,
            is_article_selected=is_article_selected
        )


@app.route('/update', methods=['GET'])
@favicon_route
def update():
    return render_template('wait.html')


@app.route('/fetch', methods=['GET'])
@favicon_route
def fetch_data():
    db.create_all()
    update_db()
    return redirect(url_for('index'))


@app.route('/test', methods=['GET'])
@favicon_route
def test():
    from breakfast_tales.parsers import get_kanobu_json
    get_kanobu_json('https://www.igromania.ru/articles/')
    return render_template('wait.html')


@app.route('/<board_slug>', methods=['GET'])
@favicon_route
def get_board(board_slug):
    with app.app_context():
        boards = Board.query.all()
        selected_board = Board.get_board_by_slug(board_slug)

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Board.get_first_feed_for_board(selected_board.id)

        articles = Feed.get_articles_for_feed(selected_feed.id, limit=30)
        is_article_selected = False
        selected_article = None
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            selected_article=selected_article,
            boards=boards,
            feeds=feeds,
            articles=articles,
            is_article_selected=is_article_selected
        )


@app.route('/<board_slug>/<feed_slug>', methods=['GET'])
@favicon_route
def get_feed(board_slug, feed_slug):
    with app.app_context():
        boards = Board.query.all()
        selected_board = Board.get_board_by_slug(board_slug)

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Feed.get_feed_by_slug(feed_slug)

        articles = Feed.get_articles_for_feed(selected_feed.id, limit=30)
        is_article_selected = False
        selected_article = None
     
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            selected_article=selected_article,
            boards=boards,
            feeds=feeds,
            articles=articles,
            is_article_selected=is_article_selected
        )


@app.route('/<board_slug>/<feed_slug>/<article_slug>', methods=['GET'])
@favicon_route
def get_article(board_slug, feed_slug, article_slug):
    with app.app_context():
        boards = Board.query.all()
        selected_board = Board.get_board_by_slug(board_slug)

        feeds = Board.get_feeds_for_board(selected_board.id)
        selected_feed = Feed.get_feed_by_slug(feed_slug)

        articles = Feed.get_articles_for_feed(selected_feed.id, limit=30)
        selected_article = Article.get_article_by_slug(article_slug)
        is_article_selected = True

        Article.set_article_as_read(selected_article)
        
        return render_template(
            'feed.html',
            title='Breakfast Tales',
            selected_board=selected_board,
            selected_feed=selected_feed,
            selected_article=selected_article,
            boards=boards,
            feeds=feeds,
            articles=articles,
            is_article_selected=is_article_selected
        )


def update_db():
    with open('boards.yml', 'r') as file:
        data = yaml.safe_load(file)
    boards = data['boards']
    for board in boards:
        Board.add_board(board['title'], board['slug'])
        for feed in board['feeds']:
            print(f"adding feed: {feed['title']}")
            if feed['type'] == 'RSS':
                raw_feed = get_rss(feed['url'])
                parse_rss(raw_feed, feed['title'], board['title'])
            elif feed['type'] == 'TJ':
                parse_tj(feed['url'], feed['title'], board['title'])
            elif feed['type'] == 'Telegram':
                parse_telegram(feed['url'], feed['title'], board['title'])
            elif feed['type'] == 'Kanobu':
                parse_kanobu(feed['url'], feed['site_url'], feed['title'], board['title'])
    print('DB updated!')
