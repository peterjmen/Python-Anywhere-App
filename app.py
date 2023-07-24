from flask import Flask, render_template

# ? On git shoudl use the imperative good i.e. "Add user page"

# instance of flask
app = Flask(__name__)


# Route decorator
@app.route("/")
def index():
    first_name = "Peter"
    words = "These are <strong>bold words</strong>"
    token_list = ["here", "is", "a", "list", "of", "words", "shoes"]
    return render_template(
        "index.html", first_name=first_name, bold_words=words, token_list=token_list
    )


@app.route("/user/<name>")  #           ⬅name from here in <>
def user(name):
    return render_template("user.html", user_name=name)


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

# did FLASK_APP=app.py
# remember requirements.txt
# source venv/scripts/activate>>
