
from helpers import common_helpers

import app_secrets
from datetime import datetime, timedelta

def date_two_days_ago():
    two_days_ago = datetime.now() - timedelta(days=2)
    return two_days_ago.strftime("%Y-%m-%d")


def filtered(string):
    string = string.lower()
    filter = ["trump", "gaza"]
    for filter_word in filter:
        if filter_word in string:
            return True
    return False


def clean_title(title):
    title = title.replace(" | TechCrunch", "")
    return title


def get_article_html(news_data):
    html = "<div class='articles'>\n"
    for article in news_data["articles"]:
        if filtered(f"{ article['title'] } { article['description'] } { article['content'] } "):
            continue

        title = clean_title(article['title'])
        html += f"<article><a href='{ article['url'] }'><h3>{ title }</a></h3>\n<p>{ article['description'] } &ndash; <em>{ article['author'] } / { article['publishedAt'] }</em></p>\n</article>\n"
    html += "</div>\n"
    return html


def main():
    html = dict()
    two_days_ago = date_two_days_ago()

    tc_url = f"https://newsapi.org/v2/everything?sources=techcrunch&from={ two_days_ago }&apiKey={ app_secrets.newsapi_key }"
    tc_news_data = common_helpers.fetch_api(tc_url)
    html["tc_articles"] = get_article_html(tc_news_data)

    nbf_url = f"https://newsapi.org/v2/everything?sources=next-big-future&from={ two_days_ago }&apiKey={ app_secrets.newsapi_key }"
    nbf_news_data = common_helpers.fetch_api(nbf_url)
    html["nbf_articles"] = get_article_html(nbf_news_data)

    tv_url = f"https://newsapi.org/v2/everything?sources=the-verge&from={ two_days_ago }&apiKey={ app_secrets.newsapi_key }"
    tv_news_data = common_helpers.fetch_api(tv_url)
    html["tv_articles"] = get_article_html(tv_news_data)

    return html
