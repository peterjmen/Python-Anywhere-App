from flask import Flask, render_template, request
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from newspaper import Article

app = Flask(__name__)
NEWS_API_KEY = "c90bf5366948496b842fa35d8776398c"


def fetch_article_content(article_url):
    article_obj = Article(article_url)
    try:
        article_obj.download()
        article_obj.parse()
        return article_obj.text
    except Exception as e:
        print(f"Failed to download article from URL: {article_url}, error: {str(e)}")
        return None


def fetch_articles(keyword=None, language="en"):
    url = f"https://newsapi.org/v2/everything?apiKey={NEWS_API_KEY}&language={language}&pageSize=10"
    if keyword:
        url += f"&q={keyword}"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch articles:", response.status_code, response.text)
        return []

    articles = response.json().get("articles", [])

    # Fetch article content concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_article_content, article["url"])
            for article in articles
        ]
        for idx, future in enumerate(futures):
            result = future.result()
            if result:
                articles[idx]["content"] = result
            else:
                articles[idx]["content"] = "Failed to fetch content"

    # Format the published date and filter out articles that failed to download
    filtered_articles = []
    for article in articles:
        if article["content"] != "Failed to fetch content":
            article["publishedAt"] = datetime.strptime(
                article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%b %d, %Y %H:%M:%S")
            filtered_articles.append(article)

    # Sort articles by publishedAt in ascending order
    sorted_articles = sorted(
        filtered_articles,
        key=lambda x: datetime.strptime(x["publishedAt"], "%b %d, %Y %H:%M:%S"),
        reverse=True,
    )

    return sorted_articles


@app.route("/", methods=["GET", "POST"])
def index():
    selected_keyword = ""
    selected_language = "en"
    articles = []

    if request.method == "POST":
        selected_keyword = request.form.get("keyword", "").strip() or None
        selected_language = request.form.get("language", "en")
        articles = fetch_articles(keyword=selected_keyword, language=selected_language)

    return render_template(
        "index.html",
        articles=articles,
        selected_keyword=selected_keyword,
        selected_language=selected_language,
    )


if __name__ == "__main__":
    app.run(debug=True)
