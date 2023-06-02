import uuid

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from slugify import slugify

db = SQLAlchemy()

class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)

    feeds = db.relationship('Feed', backref='board', primaryjoin="Board.id == Feed.board_id")

    def __init__(self, id, title, slug):
        self.id = id
        self.title = title
        self.slug = slug

    @staticmethod
    def add_board(title, slug):
        existing_board = Board.query.filter_by(slug=slug).first()
        if existing_board:
            return existing_board
        new_board = Board(
            id = uuid.uuid4().hex,
            title = title,
            slug = slug
        )
        db.session.add(new_board)
        db.session.commit()
        return new_board
    
    @staticmethod
    def get_first_board():
        return Board.query.first()
    
    @staticmethod
    def get_board_by_title(title):
        return Board.query.filter_by(title=title).first()
    
    @staticmethod
    def get_board_by_slug(slug):
        return Board.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_feeds_for_board(board_id):
        return Feed.query.filter_by(board_id=board_id).all()
    
    @staticmethod
    def get_first_feed_for_board(board_id):
        return Feed.query.filter_by(board_id=board_id).first()
    
    @staticmethod
    def get_first_board():
        return Board.query.first()


class Feed(db.Model):
    __tablename__ = 'feeds'
    
    id = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(32), nullable=False)
    subtitle = db.Column(db.Text)
    site_url = db.Column(db.String(255), nullable=False)
    feed_url = db.Column(db.String(255), nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    board_id = db.Column(db.String(255), db.ForeignKey('boards.id'), nullable=False)

    articles = db.relationship('Article', backref='feed', primaryjoin="Feed.id == Article.feed_id")

    def __init__(self, id, title, slug, subtitle, site_url, feed_url, updated, board_id):
        self.id = id
        self.title = title
        self.slug = slug
        self.subtitle = subtitle
        self.site_url = site_url
        self.feed_url = feed_url
        self.updated = updated
        self.board_id = board_id

    @staticmethod
    def add_feed(title, subtitle, site_url, feed_url, board_id):
        existing_feed = Feed.query.filter_by(feed_url=feed_url).first()
        if existing_feed:
            return existing_feed
        new_feed = Feed(
            id = uuid.uuid4().hex,
            title = title,
            slug = slugify(title, to_lower=True, max_length=32),
            subtitle = subtitle,
            site_url = site_url,
            feed_url = feed_url,
            updated = datetime.now(),
            board_id = board_id
        )
        db.session.add(new_feed)
        db.session.commit()
        return new_feed
    
    @staticmethod
    def get_feed_by_id(feed_id):
        return Feed.query.filter_by(id=feed_id).first()
    
    @staticmethod
    def get_random_feed():
        return Feed.query.order_by(db.func.random()).first()
    
    @staticmethod
    def get_feed_by_url(feed_url):
        return Feed.query.filter_by(feed_url=feed_url).first()
    
    @staticmethod
    def get_feed_by_slug(slug):
        return Feed.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_first_feed():
        return Feed.query.first()
    
    @staticmethod
    def get_articles_for_feed(feed_id):
        return Article.query.filter_by(feed_id=feed_id).all()
    

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(255), nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    thumbnail = db.Column(db.Text)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    feed_id = db.Column(db.String(255), db.ForeignKey('feeds.id'), nullable=False)

    def __init__(self, id, title, slug, description, url, feed_id, published, thumbnail, is_read=False):
        self.id = id
        self.title = title
        self.slug = slug
        self.description = description
        self.url = url
        self.feed_id = feed_id
        self.published = published
        self.thumbnail = thumbnail
        self.is_read = is_read
    
    @staticmethod
    def add_article(title, description, url, feed_id, published, thumbnail):
        existing_article = Article.query.filter_by(url=url).first()
        if existing_article:
            return existing_article
        slug_head = slugify(title, to_lower=True, max_length=16)
        id = uuid.uuid4().hex
        new_article = Article(
            id = id,
            title = title,
            slug = f"{slug_head}-{id}",
            description = description,
            url = url,
            feed_id = feed_id,
            published = published,
            thumbnail = thumbnail,
            is_read = False
        )
        db.session.add(new_article)
        db.session.commit()
        return new_article
    
    @staticmethod
    def get_last_articles(feed_id, limit):
        articles = Article.query \
            .filter_by(feed_id=feed_id) \
            .order_by(Article.published.desc()) \
            .limit(limit) \
            .all()
        return articles
    
    @staticmethod
    def get_article_by_id(article_id):
        return Article.query.filter_by(id=article_id).first()
    
    @staticmethod
    def get_article_by_slug(article_slug):
        return Article.query.filter_by(slug=article_slug).first()
    
    
def make_id():
    id = uuid.uuid4()
    return id.hex
