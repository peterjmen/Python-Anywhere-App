from flask import Flask, render_template, request
import requests
from newspaper import Article
from datetime import datetime

app = Flask(__name__)
NEWS_API_KEY = "c90bf5366948496b842fa35d8776398c"

COUNTRIES = [
    "us",  # United States
    "gb",  # United Kingdom
    "ca",  # Canada
    "au",  # Australia
    "in",  # India
    "za",  # South Africa
    "nz",  # New Zealand
    "sg",  # Singapore
    "ie",  # Ireland
    "ph",  # Philippines
]

KEYWORDS = ["New Zealand"]

CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology",
]


def fetch_sources(country=None):
    url = f"https://newsapi.org/v2/sources?apiKey={NEWS_API_KEY}&language=en"
    if country and country != "all":
        url += f"&country={country}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json().get("sources", [])


def fetch_articles(
    country="us",
    category="general",
    keyword="New Zealand",
    from_date=None,
    to_date=None,
):
    sources = [source["id"] for source in fetch_sources(country)]
    sources = ",".join(sources)

    url = f"https://newsapi.org/v2/everything?apiKey={NEWS_API_KEY}&language=en&pageSize=100&sources={sources}"

    if category != "all":
        url += f"&category={category}"

    if keyword and keyword != "All":
        url += f"&qInTitle={keyword}"

    if from_date:
        url += f"&from={from_date}"

    if to_date:
        url += f"&to={to_date}"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch articles:")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return []
    articles = response.json().get("articles", [])

    for article in articles:
        article["publishedAt"] = datetime.strptime(
            article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%b %d, %Y %H:%M:%S")

    return sorted(articles, key=lambda x: x["publishedAt"], reverse=True)


@app.route("/", methods=["GET", "POST"])
def index():
    selected_country = "nz"
    selected_category = "all"
    selected_keyword = "New Zealand"
    sources = fetch_sources()
    articles = []

    if request.method == "POST":
        selected_country = request.form.get("country", "nz")
        selected_category = request.form.get("category", "all")
        selected_keyword = request.form.get("keyword", "New Zealand")
        articles = fetch_articles(selected_country, selected_category, selected_keyword)

        for article in articles:
            try:
                article_url = article.get("url", "")
                article_obj = Article(article_url)
                article_obj.download()
                article_obj.parse()
                article["content"] = article_obj.text
            except Exception as e:
                article["content"] = "Failed to fetch content"

    return render_template(
        "index.html",
        articles=articles,
        sources=sources,
        countries=COUNTRIES,
        keywords=KEYWORDS,
        categories=CATEGORIES,
        selected_country=selected_country,
        selected_category=selected_category,
        selected_keyword=selected_keyword,
    )


if __name__ == "__main__":
    app.run(debug=True)
