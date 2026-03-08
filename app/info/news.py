from helpers import common_helpers

import app_secrets
from datetime import datetime, timedelta
import pytz
from urllib.parse import urlsplit, urlunsplit, quote

from pydantic import BaseModel, ValidationError
from typing import List
from openai import OpenAI
import json
import xml.etree.ElementTree as ET
import requests
import sys


def select_articles_with_ai(news_articles):
    """Selects relevant articles with AI.

    Args:
        news_articles (list): A list of news articles.

    Returns:
        NewsArticlesResponse: A response object containing the selected articles.
    """
    print("Selecting articles with AI")
    client = OpenAI()

    class NewsArticle(BaseModel):
        title: str
        link: str
        introduction: str

    class NewsArticlesResponse(BaseModel):
        articles: List[NewsArticle]

    # Convert news_articles to a JSON string if it isn't already
    news_json = json.dumps(news_articles)

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "You are provided JSON with trending technology news article headlines and short introductions. Your task is to curate a selection of 2-4 headlines that are relevant for software product managers and web developers. Exclude any news articles related to shopping, home appliances, or U.S. politics. Sort results from most to least relevant."},
            {"role": "user", "content": news_json},
        ],
        response_format=NewsArticlesResponse,
    )

    print("Done selecting articles with AI")
#    print("DEBUG completion: ", completion)
    return completion.choices[0].message.parsed


def date_two_days_ago():
    """Returns the date two days ago in YYYY-MM-DD format.

    Returns:
        str: The date two days ago in YYYY-MM-DD format.
    """
    two_days_ago = datetime.now() - timedelta(days=2)
    return two_days_ago.strftime("%Y-%m-%d")


# Filters out news that contain keywords or seem to be about shopping
def filtered(string):
    """Filters out news that contain keywords or seem to be about shopping

    Args:
        string (str): The string to filter.

    Returns:
        bool: True if the article should be filtered out, False otherwise.
    """
    string = string.lower()
    filter = {
        "trump": 5,
        "republican": 5,
        "far-right": 5,
        "presidential": 5,
        "gaza": 5,
        "musk": 5,
        "elon": 5,
        "$": 1,
        " off": 1,
        "shopping": 1,
        "deals ": 1.5,
        "buy ": 1,
        "gadget": 1,
        "record low": 2,
        "record high": 2
    }
    score = 0
    for filter_word, value in filter.items():
        if filter_word in string:
            score += value

    if score >= 3:
        return True
    else:
        return False


def filter_json(json):
    """Filters out news that contain keywords or seem to be about shopping

    Args:
        json (dict): JSON response from News API containing article data.
        Key "articles" should have a list of article dictionaries.
        Each article should have: title, url, description, author, publishedAt.

    Returns:
        bool: True if the article should be filtered out, False otherwise.
    """
    filtered_articles = []
    if "articles" in json:
        for article in json["articles"]:
            # Skip articles that get a high score from the filtered function
            if filtered(f"{ article['title'] } { article['description'] } { article['content'] } "):
                continue

            article["title"] = clean_title(article["title"])
            filtered_articles.append(article)

    return filtered_articles


def clean_title(title):
    """Cleans the title of an article by removing unwanted suffixes.

    Args:
        title (str): The original title of the article.

    Returns:
        str: The cleaned title with unwanted suffixes removed.
    """
    title = title.replace(" | TechCrunch", "")
    return title


def sanitize_url(raw_url):
    """Sanitizes untrusted URLs to safe http(s) links.

    Args:
        raw_url (str): Untrusted URL from external sources.

    Returns:
        str: Sanitized URL if valid, otherwise '#'.
    """
    if not raw_url:
        return "#"

    raw_url = raw_url.strip()
    parts = urlsplit(raw_url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return "#"

    safe_path = quote(parts.path, safe="/%._-~")
    safe_query = quote(parts.query, safe="=&%._-~")
    return urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, ""))


def get_article_data(news_articles):
    """Converts article objects into sanitized data for Jinja rendering.

    Args:
        news_articles: Either a NewsArticlesResponse object or a list of NewsArticle objects.

    Returns:
        list: List of dictionaries with sanitized article fields.
    """
    if not news_articles:
        return []

    articles_to_process = news_articles.articles if hasattr(news_articles, 'articles') else news_articles

    articles = []
    for article in articles_to_process:
        articles.append({
            "title": getattr(article, "title", "") or "",
            "link": sanitize_url(getattr(article, "link", "")),
            "introduction": getattr(article, "introduction", "") or "",
        })
    return articles


def format_mit_datetime_to_finnish(datetime_string):
    """Formats a datetime string from MIT News to Finnish format and time zone.

    Args:
        datetime_string (str): The datetime string to format.

    Returns:
        str: The formatted datetime string.
    """
    # Parse the input datetime string
    dt = datetime.strptime(datetime_string, "%a, %d %b %Y %H:%M:%S %z")

    # Convert to Helsinki timezone
    helsinki_tz = pytz.timezone("Europe/Helsinki")
    dt_helsinki = dt.astimezone(helsinki_tz)

    # Format the datetime as required
    formatted_datetime = dt_helsinki.strftime("%Y-%m-%d, %H.%M")

    return formatted_datetime


def get_rss_data(rss_data):
    """Converts RSS feed data into sanitized article data.

    Args:
        rss_data (str): The RSS feed data to convert.

    Returns:
        list: List of dictionaries with sanitized article fields.
    """
    root = ET.fromstring(rss_data)

    limit = 5
    i = 0
    articles = []
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        pub_date = format_mit_datetime_to_finnish(item.find('pubDate').text)
        description = item.find('description').text

        articles.append({
            "title": f"{ pub_date }: { title }",
            "link": sanitize_url(link),
            "introduction": description or "",
        })
        i += 1
        if i >= limit:
            break
    return articles


def fetch_rss(rss_url, log = False):
    """Fetches RSS data from a URL.

    Args:
        rss_url (str): The URL of the RSS feed.
        log (bool): Whether to log the URL.

    Returns:
        str: The RSS data.
    """
    if log:
        print_log(rss_url)

    try:
        r = requests.get(rss_url)
        return r.text
    except ConnectionError:
        print(f"ERROR: complete error: {rss_url}", file=sys.stdout)
        return ""


def main():
    html_data = dict()
    two_days_ago = date_two_days_ago()

    # TechCrunch
    tc_url = f"https://newsapi.org/v2/everything?sources=techcrunch&from={ two_days_ago }&pageSize=10&apiKey={ app_secrets.newsapi_key }"
#    print(tc_url) # debug
    tc_news_data = common_helpers.fetch_api(tc_url)
    tc_news_articles = filter_json(tc_news_data)
    tc_news_selected_articles = select_articles_with_ai(tc_news_articles)
    html_data["tc_articles"] = get_article_data(tc_news_selected_articles)

    # The Verge
    tv_url = f"https://newsapi.org/v2/everything?sources=the-verge&from={ two_days_ago }&pageSize=10&apiKey={ app_secrets.newsapi_key }"
#    print(tv_url) # debug
    tv_news_data = common_helpers.fetch_api(tv_url)
    tv_news_articles = filter_json(tv_news_data)
    tv_news_selected_articles = select_articles_with_ai(tv_news_articles)
    html_data["tv_articles"] = get_article_data(tv_news_selected_articles)

    # MIT AI News
    # Note: This is not a news API, but a RSS feed, so its handled differently.
    mit_url = "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"
    mit_news_data = fetch_rss(mit_url)
    html_data["mit_articles"] = get_rss_data(mit_news_data)

    return html_data

