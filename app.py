from flask import Flask, render_template

# instance of flask
app = Flask(__name__)


# Route decorator
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/user/<name>")
def user(name):
    return "<h1>Hello {} 😉<h1>".format(name)


if __name__ == "__main__":
    app.run(debug=True)

# did FLASK_APP=app.py
# remember requirements.txt
# source venv/scripts/activate>>
