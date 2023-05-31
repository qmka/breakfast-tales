import feedparser

from bs4 import BeautifulSoup
from datetime import datetime

from breakfast_tales.models import Feed
from breakfast_tales.models import Article


# Получить RSS с сайта
def get_rss(url):
    feed = feedparser.parse(url)
    return feed


def parse_rss(feed):
    # Добавляем фид
    new_feed = Feed.add_feed(
        feed.feed.title,
        feed.feed.subtitle,
        feed.feed.link,
        feed.href
    )

    # Добавляем статьи фида
    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        description = soup.get_text()
        Article.add_article(
            entry.title,
            description,
            entry.link,
            new_feed.id,
            convert_to_datetime(entry.published),
            get_thumbnail(entry.summary)
        )


def get_thumbnail(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    img_tag = soup.find('img')
    if img_tag:
        src = img_tag.get('src')
        return src
    else:
        return ''


def convert_to_datetime(str_date):
    datetime_format = '%a, %d %b %Y %H:%M:%S %z'
    return datetime.strptime(str_date, datetime_format)