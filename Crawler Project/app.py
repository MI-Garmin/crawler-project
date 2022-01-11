from flask import Flask, render_template
import sqlite3 as sql

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movie")
def movie():
    datalist = []
    conn = sql.connect("movie.db")
    cur = conn.cursor()
    query = "SELECT * FROM movie250"
    data = cur.execute(query)
    for items in data:
        datalist.append(items)
    cur.close()
    conn.close()
    return render_template("movie.html", data=datalist)


@app.route("/score")
def score():
    mark = []
    num = []
    conn = sql.connect("movie.db")
    cur = conn.cursor()
    query = "SELECT rating, COUNT(*) FROM movie250 GROUP BY rating"
    data = cur.execute(query)
    for items in data:
        mark.append(items[0])
        num.append(items[1])

    cur.close()
    conn.close()
    return render_template("score.html", mark=mark, num=num)


@app.route("/word")
def wordcloud():
    return render_template("wordcloud.html")


if __name__ == "__main__":
    app.run(debug=True)
