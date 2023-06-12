import feedparser
import requests
import json
import io

from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent

from breakfast_tales.models import Board
from breakfast_tales.models import Feed
from breakfast_tales.models import Article


# Получить RSS с сайта
def get_rss(url):
    feed = feedparser.parse(url)
    return feed


def parse_rss(feed, board_title):
    # Добавляем фид
    new_feed = Feed.add_feed(
        feed.feed.title,
        feed.feed.subtitle,
        feed.feed.link,
        feed.href,
        Board.get_board_by_title(board_title).id
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


def convert_to_datetime_tj(str_date):
    datetime_format = '%d-%m-%y'
    return datetime.strptime(str_date, datetime_format)


def parse_tj(url, board_title):
    tj = get_tj_json(url)
    # title, subtitle, site_url, feed_url, board_id

    new_feed = Feed.add_feed(
        tj['title'],
        tj['description'],
        url,
        url,
        Board.get_board_by_title(board_title).id
    )

    for card in tj['cards']:
        article = card['article']
        article_url = f"{url[:-1]}{article['path']}"
        article_description = article['excerpt']
        # article_description = make_tj_article_description(article_url)
        if not card['media']['backgroundImage']:
            thumbnail_url = card['media']['image']['files']['original']['filepath']
        else:
            thumbnail_url = card['media']['backgroundImage']['files']['original']['filepath']

        Article.add_article(
            article['title'],
            article_description,
            article_url,
            new_feed.id,
            convert_to_datetime_tj(article['date_published']),
            thumbnail_url
        )


def make_tj_article_description(url):
    raw_content = safe_download(url)

    with open('example.html', 'a', encoding='utf-8') as f:
        f.write(raw_content)

    soup = BeautifulSoup(raw_content, "html.parser")

    # Находим элемент с классом "article"
    article_body = soup.find('main')
    if article_body:
        for element in article_body.find_all(recursive=False):
            element.extract()
        useful_text = article_body.get_text(separator='\n').strip()
        return useful_text
    else:
        return None


def get_tj_json(url):
    raw_content = download(url)

    '''with open('example.html', 'a', encoding='utf-8') as f:
        f.write(raw_content)'''

    soup = BeautifulSoup(raw_content, "html.parser")
    

    hidden_json_content = soup.find('script', {'type': 'application/json', 'data-id': 'flow-page'})
    json_data = json.loads(hidden_json_content.string)


    with open('example_json.json', 'a', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False)
    
    return json_data


def download(url):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text

    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)


def safe_download(url):
    MAX_PARSABLE_CONTENT_LENGTH = 15 * 1024 * 1024
    try:
        response = requests.get(
            url=url,
            timeout=5,
            headers={'User-Agent': UserAgent().chrome},
            stream=True  # the most important part — stream response to prevent loading everything into memory
        )
    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)
    response.encoding = 'utf-8'
    html = io.StringIO()
    total_bytes = 0

    for chunk in response.iter_content(chunk_size=100 * 1024, decode_unicode=True):
        total_bytes += len(chunk)
        if total_bytes >= MAX_PARSABLE_CONTENT_LENGTH:
            return ""  # reject too big pages
        html.write(chunk)

    return html.getvalue()