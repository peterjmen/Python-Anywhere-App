# ---------------------------------------------
# TODO: Activate the virtual environment
# ➡➡➡ source venv/Scripts/activate ⬅⬅⬅
# ls -R > file_structure.txt
# ---------------------------------------------

import os
from flask import Flask, render_template, request
import requests
from datetime import datetime
import joblib
import mysql.connector

db_config = {
    "user": "Manhandle",
    "password": "givemedata",
    "host": "Manhandle.mysql.pythonanywhere-services.com",
    "database": "Manhandle$pdbase",
    "raise_on_warnings": True
}


app = Flask(__name__)
NEWS_API_KEY = "c90bf5366948496b842fa35d8776398c"

# Load the trained model
# model_filename = os.path.join(
#     "/home/Manhandle/Python-Anywhere-App", "sentiment_model.pkl"


# if sentiment_model.pkl is in the same directory  script
model_filename = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")


model = joblib.load(model_filename)
print(f"Trained model loaded from '{model_filename}'")

# send info to database
def insert_sentiment_to_db(sentiment, sentiment_value, article_headline):
    cursor = None
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO sentifeed_data(sentiment, sentiment_value, article_headline) VALUES (%s, %s, %s)"
        cursor.execute(query, (sentiment, sentiment_value, article_headline))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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


def fetch_articles(country=None, category=None, sentiment=None):
    print(
        f"Fetching articles for country: {country} and category: {category}"
    )  # Debug print

    url = f"https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}&pageSize=100"

    if country and country != "":
        url += f"&country={country}"

    if category:
        url += f"&category={category}"

    # Add language parameter for English
    url += "&language=en"

    response = requests.get(url)
    print(f"Response status code: {response.status_code}")  # Debug print

    if response.status_code != 200:
        print("Failed to fetch articles:", response.status_code, response.text)
        return []

    articles = response.json().get("articles", [])

    # Format the published date and analyze sentiment
    for article in articles:
        article["content"] = article["content"] or "No content available"
        article["publishedAt"] = datetime.strptime(
            article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%b %d, %Y %H:%M:%S")

        sentiment_weighting = calculate_sentiment(article["content"])
        sentiment_category = sentiment_to_category(sentiment_weighting)

        article["sentiment_weighting"] = sentiment_weighting
        article["sentiment_category"] = sentiment_category

    # Sort articles by publishedAt in descending order
    sorted_articles = sorted(
        articles,
        key=lambda x: datetime.strptime(x["publishedAt"], "%b %d, %Y %H:%M:%S"),
        reverse=True,
    )

    # Filter articles based on the selected sentiment
    if sentiment and sentiment != "All":
        filtered_articles = [
            article
            for article in sorted_articles
            if article["sentiment_category"] == sentiment
        ]
    else:
        filtered_articles = sorted_articles

    return filtered_articles


@app.route("/", methods=["GET", "POST"])
def index():
    selected_country = None
    selected_category = None
    selected_sentiment = None
    articles = []

    if request.method == "POST":
        selected_country = request.form.get("country", "").strip()
        if selected_country == "":
            selected_country = None  # Set to None if All/World selected
        selected_category = request.form.get("category", "").strip() or None
        selected_sentiment = request.form.get("sentiment-filter", "").strip() or None
        articles = fetch_articles(
            country=selected_country,
            category=selected_category,
            sentiment=selected_sentiment,
        )

    return render_template(
        "index.html",
        articles=articles,
        selected_country=selected_country,
        selected_category=selected_category,
        selected_sentiment=selected_sentiment,
    )

@app.route("/submit-rating", methods=["POST"])
def submit_rating():
    try:
        sentiment = request.form["sentiment"]
        article_title = request.form["article_title"]

        sentiment_map = {
            "Very Positive": 4,
            "Positive": 3,
            "Neutral": 2,
            "Negative": 1,
            "Very Negative": 0
        }

        insert_sentiment_to_db(sentiment, sentiment_map[sentiment], article_title)
        return "Rating submitted!", 200

    except Exception as e:
        print(f"Error encountered: {e}")
        return "An error occurred while processing your request.", 500


if __name__ == "__main__":
    app.run(debug=True)
