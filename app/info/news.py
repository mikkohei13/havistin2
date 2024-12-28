from helpers import common_helpers

import app_secrets
from datetime import datetime, timedelta

from pydantic import BaseModel, ValidationError
from typing import List
from openai import OpenAI
import json


def select_articles_with_ai(news_articles):
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
        "gaza": 5,
        "musk": 5,
        "elon": 5,
        "$": 1,
        " off": 1,
        "shopping": 1,
        "deals ": 1.5,
        "buy ": 1,
        "gadget": 1,
        "record low": 3,
        "record high": 2.5
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


def get_article_html(news_articles):
    """Converts news API data into HTML markup for displaying articles.

    Args:
        news_articles: Either a NewsArticlesResponse object or a list of NewsArticle objects.

    Returns:
        str: HTML markup containing formatted article listings wrapped in a div.
            Returns "Rate limited" message if no articles are present.
    """
    if not news_articles:
        return "<div class='articles'>\nRate limited\n</div>\n"

    # Get the articles list from the response
    articles_to_process = news_articles.articles if hasattr(news_articles, 'articles') else news_articles

    html = "<div class='articles'>\n"
    for article in articles_to_process:
        html += "<article>\n"
        html += f"    <h3><a href='{ article.link }'>{ article.title }</a></h3>\n"
        html += f"    <p>{ article.introduction }</p>\n"
        html += "</article>\n"
    html += "</div>\n"
    return html


def main():
    html = dict()
    two_days_ago = date_two_days_ago()

    # TechCrunch
    tc_url = f"https://newsapi.org/v2/everything?sources=techcrunch&from={ two_days_ago }&pageSize=10&apiKey={ app_secrets.newsapi_key }"
    print(tc_url)
    tc_news_data = common_helpers.fetch_api(tc_url)
    tc_news_articles = filter_json(tc_news_data)
    tc_news_selected_articles = select_articles_with_ai(tc_news_articles)
    html["tc_articles"] = get_article_html(tc_news_selected_articles)

    # The Verge
    tv_url = f"https://newsapi.org/v2/everything?sources=the-verge&from={ two_days_ago }&pageSize=10&apiKey={ app_secrets.newsapi_key }"
    print(tv_url)
    tv_news_data = common_helpers.fetch_api(tv_url)
    tv_news_articles = filter_json(tv_news_data)
    tv_news_selected_articles = select_articles_with_ai(tv_news_articles)
    html["tv_articles"] = get_article_html(tv_news_selected_articles)

    return html
