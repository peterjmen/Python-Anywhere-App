# ---------------------------------------------
# TODO: Activate the virtual environment
# ➡➡➡ source venv/Scripts/activate ⬅⬅⬅
# ls -R > file_structure.txt
# ---------------------------------------------

from flask import Flask, render_template, request
from templates.sample_news import sample_news

app = Flask(__name__)


@app.context_processor
def utility_processor():
    def get_sentiment_category(rating):
        if rating == "All":
            return "All"
        rating = int(rating)
        if rating == 0:
            return "Very Negative"
        elif rating == 1:
            return "Negative"
        elif rating == 2:
            return "Neutral"
        elif rating == 3:
            return "Positive"
        elif rating == 4:
            return "Very Positive"
        else:
            return "Unknown"

    return dict(get_sentiment_category=get_sentiment_category)


@app.route("/", methods=["GET", "POST"])
def index():
    selected_article = None
    filtered_news = sample_news  # Show all news by default
    sentiment_filter = "All"  # Default sentiment filter value
    category_filter = "All"  # Default category filter value
    country_filter = "All"  # Default country filter value

    if request.method == "POST":
        # Sentiment Filter
        sentiment_filter = request.form.get("sentiment", "All")

        if sentiment_filter != "All":
            sentiment_rating = [
                "Very Negative",
                "Negative",
                "Neutral",
                "Positive",
                "Very Positive",
            ].index(sentiment_filter)
            filtered_news = [
                news
                for news in sample_news
                if news.get("rated_sentiment") == sentiment_rating
            ]

        # Category Filter
        category_filter = request.form.get("category", "All")

        if category_filter != "All":
            filtered_news = [
                news
                for news in filtered_news
                if news.get("category") == category_filter
            ]

        # Country Filter
        country_filter = request.form.get("country", "All")

        if country_filter != "All":
            filtered_news = [
                news for news in filtered_news if news.get("country") == country_filter
            ]

        selected_article = request.form.get("selected_article")

    return render_template(
        "index.html",
        news=filtered_news,
        selected_article=selected_article,
        sentiment_filter=sentiment_filter,
        category_filter=category_filter,
        country_filter=country_filter,
    )


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
