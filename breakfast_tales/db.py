from datetime import datetime
import sqlite3
import uuid

DATABASE = 'base.db'


def create_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feeds
                  (id TEXT PRIMARY KEY NOT NULL,
                  title TEXT NOT NULL,
                  subtitle TEXT,
                  site_url TEXT NOT NULL,
                  feed_url TEXT NOT NULL,
                  updated DATETIME NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles
                  (id TEXT PRIMARY KEY NOT NULL,
                  title TEXT NOT NULL,
                  description TEXT NOT NULL,
                  url TEXT NOT NULL,
                  feed TEXT NOT NULL,
                  published DATETIME NOT NULL,
                  thumbnail TEXT NOT NULL,
                  FOREIGN KEY (feed) REFERENCES feeds(feed_url))''')
    conn.close()
    

def add_feed_to_db(feed):
    operation_status = False
    feed_url = feed['feed_url']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM feeds WHERE feed_url=?", (feed_url,))
    existing_feed = cursor.fetchone()
    if existing_feed is None:
        updated = datetime.now()
        cursor.execute(f"INSERT INTO feeds (id, title, subtitle, site_url, feed_url, updated) VALUES (?, ?, ?, ?, ?, ?)",
                       (feed['id'], feed['title'], feed['subtitle'], feed['site_url'], feed_url, updated))
        conn.commit()
        operation_status = True
    conn.close()
    return operation_status


def add_article_to_db(article):
    operation_status = False
    article_url = article['url']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM articles WHERE url=?", (article_url,))
    existing_feed = cursor.fetchone()
    if existing_feed is None:
        cursor.execute(f"INSERT INTO articles (id, title, description, url, feed, published, thumbnail) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (article['id'], article['title'], article['description'], article['url'], article['feed'], article['published'], article['thumbnail']))
        conn.commit()
        operation_status = True
    conn.close()
    return operation_status


def get_feed_from_db(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM feeds WHERE id=?", (id,))
    feed = cursor.fetchone()
    if feed is not None:
        _, title, subtitle, site_url, feed_url, updated = feed
        # id, feed['title'], feed['subtitle'], feed['site_url'], feed_url, updated)
        feed_data = {
            'id': id,
            'title': title,
            'subtitle': subtitle,
            'site_url': site_url,
            'feed_url': feed_url,
            'updated': updated
        }
    else:
        feed_data = None
    return feed_data


def get_feed_id_by_feed_url(feed_url):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM feeds WHERE feed_url=?", (id,))
    feed = cursor.fetchone()
    return feed[0]


def get_article_by_id(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM articles WHERE id=?", (id,))
    article = cursor.fetchone()
    if article is not None:
        _, title, description, url, feed, published, thumbnail = article
        article_data = {
            'id': id,
            'title': title,
            'description': description,
            'url': url,
            'feed': feed,
            'published': published,
            'thumbnail': thumbnail
        }
    else:
        article_data = None
    return article_data


def get_articles_from_feed(feed_id, count):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = """
    SELECT id, title, description, url, feed, published, thumbnail
    FROM articles
    WHERE feed = ?
    ORDER BY published DESC
    LIMIT ?
    """
    cursor.execute(query, (feed_id, count))
    articles = cursor.fetchall()
    articles_data = []
    for article in articles:
        article_data = {
            'id': article[0],
            'title': article[1],
            'url': article[3],
            'published': article[5],
            'description': article[2],
            'thumbnail': article[6],
            'feed': article[4]
        }
        articles_data.append(article_data)
    return articles_data


def make_id():
    id = uuid.uuid4()
    return id.hex

# create_db()

# get_articles_from_feed('590e2982b31e477d8f6467835959dd31', 5)