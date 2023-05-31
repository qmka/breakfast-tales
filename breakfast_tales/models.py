import uuid

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Feed(db.Model):
    __tablename__ = 'feeds'
    
    id = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text)
    site_url = db.Column(db.String(255), nullable=False)
    feed_url = db.Column(db.String(255), nullable=False)
    updated = db.Column(db.DateTime, nullable=False)

    articles = db.relationship('Article', backref='feed', primaryjoin="Feed.id == Article.feed_id")

    def __init__(self, id, title, subtitle, site_url, feed_url, updated):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.site_url = site_url
        self.feed_url = feed_url
        self.updated = updated

    @staticmethod
    def add_feed(title, subtitle, site_url, feed_url):
        existing_feed = Feed.query.filter_by(feed_url=feed_url).first()
        if existing_feed:
            return existing_feed
        new_feed = Feed(
            id = uuid.uuid4().hex,
            title = title,
            subtitle = subtitle,
            site_url = site_url,
            feed_url = feed_url,
            updated = datetime.now()
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
    

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.String(255), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(255), nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    thumbnail = db.Column(db.Text)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    feed_id = db.Column(db.String(255), db.ForeignKey('feeds.id'), nullable=False)

    def __init__(self, id, title, description, url, feed_id, published, thumbnail, is_read=False):
        self.id = id
        self.title = title
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
        new_article = Article(
            id = uuid.uuid4().hex,
            title = title,
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
    
    
def make_id():
    id = uuid.uuid4()
    return id.hex
