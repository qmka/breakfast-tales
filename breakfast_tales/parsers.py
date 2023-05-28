import feedparser
import uuid

from bs4 import BeautifulSoup

from breakfast_tales.db import add_feed_to_db
from breakfast_tales.db import add_article_to_db


# Получить RSS с сайта
def get_rss(url):
    feed = feedparser.parse(url)
    return feed


def parse_rss(feed):
    # Создаём промежуточный объект хранения данных
    feed_id = make_id()
    feed_data = {
        'id': feed_id,
        'title': feed.feed.title,
        'subtitle': feed.feed.subtitle,
        'site_url': feed.feed.link,
        'feed_url': feed.href,
    }

    # Отправляем фид в базу данных
    add_feed_to_db(feed_data)

    # Обрабатываем статьи фида
    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        description = soup.get_text()
        article_data = {
            'id': make_id(),
            'title': entry.title,
            'url': entry.link,
            'published': entry.published,
            'description': description,
            'thumbnail': get_thumbnail(entry.summary),
            'feed': feed_id
        }
        add_article_to_db(article_data)
        # Отправляем статью в базу данных


def get_thumbnail(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    img_tag = soup.find('img')
    if img_tag:
        src = img_tag.get('src')
        return src
    else:
        return ''
    
def make_id():
    id = uuid.uuid4()
    return id.hex