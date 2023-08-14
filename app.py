# ---------------------------------------------
# TODO: Activate the virtual environment
# ➡➡➡ source venv/Scripts/activate ⬅⬅⬅
# ls -R > file_structure.txt
# ---------------------------------------------

from flask import Flask, render_template, request
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from newspaper import Article
import joblib

app = Flask(__name__)
NEWS_API_KEY = "c90bf5366948496b842fa35d8776398c"

# Load the trained model
model_filename = "sentiment_model.pkl"
model = joblib.load(model_filename)
print(f"Trained model loaded from '{model_filename}'")


# Sentiment prediction
def calculate_sentiment(text):
    probs = model.predict_proba([text])
    sentiment_value = 0 * probs[0][0] + 4 * probs[0][1]
    return sentiment_value


def sentiment_to_category(sentiment_value):
    if sentiment_value <= 0.5:
        return "Very Negative"
    elif sentiment_value <= 1.5:
        return "Negative"
    elif sentiment_value <= 2.5:
        return "Neutral"
    elif sentiment_value <= 3.5:
        return "Positive"
    else:
        return "Very Positive"


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

            # Calculate sentiment weighting and category
            sentiment_weighting = calculate_sentiment(article["content"])
            sentiment_category = sentiment_to_category(sentiment_weighting)

            article[
                "sentiment_weighting"
            ] = sentiment_weighting  # Rounded to 1 decimal place
            article["sentiment_category"] = sentiment_category

            filtered_articles.append(article)

    # Sort articles by publishedAt in ascending order
    sorted_articles = sorted(
        filtered_articles,
        key=lambda x: datetime.strptime(x["publishedAt"], "%b %d, %Y %H:%M:%S"),
        reverse=True,
    )

    return sorted_articles


@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    selected_keyword = ""
    selected_language = "en"
    selected_sentiment = "all"  # Add this line
    articles = []
    sentiment_predictions = []  # List to store sentiment predictions for articles

    if request.method == "POST":
        selected_keyword = request.form.get("keyword", "").strip() or None
        selected_language = request.form.get("language", "en")
        selected_sentiment = request.form.get(
            "sentiment-filter", "all"
        )  # Add this line
        articles = fetch_articles(keyword=selected_keyword, language=selected_language)

        # Perform sentiment prediction for each article's content
        for article in articles:
            sentiment_prediction = model.predict([article["content"]])[0]
            sentiment_predictions.append(sentiment_prediction)
            article["sentiment"] = sentiment_prediction

    return render_template(
        "index.html",
        articles=articles,
        sentiment_predictions=sentiment_predictions,
        selected_keyword=selected_keyword,
        selected_language=selected_language,
        selected_sentiment=selected_sentiment,  # Add this line
    )


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
