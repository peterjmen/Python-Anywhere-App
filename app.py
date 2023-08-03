# ! *^*^*^*^*^**^*^*^*^*^**^*^*^*^*^*^*^**^*^*^*^*^*^*^ #
# TODO *^*^*^*^*^**^*^*^*^**^*^*^*^*^*^*^*^**^*^*^*^*^* #
# * 👉 ➡➡➡ source venv/Scripts/activate ⬅⬅⬅ 👈    #
# TODO *^*^*^*^*^**^*^*^*^**^*^*^*^*^**^*^*^*^**^*^*^*^ #
# ! *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^^*^*^*^*^*^*^*^*^*^ #


from flask import Flask, render_template, request

app = Flask(__name__)

# Sample news data (you can replace this with real data from NewsAPI)
sample_news = [
    {
        "headline": "Sad News 1",
        "category": "Politics",
        "country": "UK",
        "sentiment": "Negative",
        "rated_sentiment": 0,  # Rating: 0 (Very Negative)
        "content": "Today's political news in the UK was filled with disappointment and sadness. The developments in the political landscape left citizens feeling disheartened and unsatisfied with the outcomes. It seems like there's no end to the mehness in the political realm lately..."
    },
    {
        "headline": "Meh News 2",
        "category": "Sports",
        "country": "Australia",
        "sentiment": "Negative",
        "rated_sentiment": 1,  # Rating: 1 (Negative)
        "content": "This is a meh news article about meh news in the sports world. It seems like there was not much excitement or thrill in today's sports events. Fans were left feeling indifferent and unimpressed with the outcomes. The lack of intense competition and captivating moments made it a meh day for sports enthusiasts."
    },
    {
        "headline": "Neutral News 3",
        "category": "Entertainment",
        "country": "Canada",
        "sentiment": "Neutral",
        "rated_sentiment": 2,  # Rating: 2 (Neutral)
        "content": "Today's entertainment news was quite meh. There were no groundbreaking announcements or scandals that grabbed people's attention. Instead, the news consisted of average updates about celebrities and the entertainment industry, leaving readers with a sense of neutrality and indifference."
    },
    {
        "headline": "Decent News 4",
        "category": "Health",
        "country": "Germany",
        "sentiment": "Positive",
        "rated_sentiment": 3,  # Rating: 3 (Positive)
        "content": "In the health sector, there were some decent news and developments in Germany. Progress was made in various areas, offering hope and optimism for better healthcare in the future. Although it was not groundbreaking news, the positive strides in health-related matters brought a sense of contentment and satisfaction."
    },
    {
        "headline": "Happy News 5",
        "category": "Technology",
        "country": "USA",
        "sentiment": "Very Positive",
        "rated_sentiment": 4,  # Rating: 4 (Very Positive)
        "content": "Today's technology news was filled with exciting and innovative breakthroughs in the USA. From cutting-edge gadgets to revolutionary advancements, tech enthusiasts were delighted by the positive developments. The tech industry has certainly been thriving, and the news brought joy and happiness to all those following the latest trends and innovations."
    }
]

def get_sentiment_category(rating):
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


@app.route("/", methods=["GET", "POST"])
def index():
    selected_article = None
    if request.method == "POST":
        sentiment_filter = request.form.get("sentiment")
        if sentiment_filter == "All":
            filtered_news = sample_news
        else:
            sentiment_rating = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"].index(sentiment_filter)
            filtered_news = [news for news in sample_news if news.get("rated_sentiment") == sentiment_rating]
        selected_article = request.form.get("selected_article")
    else:
        filtered_news = sample_news  # Show all news by default

    return render_template("index.html", news=filtered_news, selected_article=selected_article, get_sentiment_category=get_sentiment_category)

@app.route('/user/<name>')
def user(name):
    # your code here
    return render_template('user.html', name=name)


    # Custom error pages
# flask mechanism to handle errors:

# invalid url ⬇
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
