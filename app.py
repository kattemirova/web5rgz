from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2


app = Flask(__name__)

app.secret_key = "123"

def dbConnect():
    conn = psycopg2.connect(
        host = "127.0.0.1",
        database = "temirova_rgz",
        user = "rgz_temirova",
        password = "123"
    )
    return conn;

def dbClose(cursor, connection):
    cursor.close()
    connection.close()


@app.route("/")
def main():
    username = "Anon"
    return render_template ('base.html', username=username)

@app.route('/register', methods=["GET", "POST"])
def registerPage():
    errors = ''

    if request.method == "GET":
        return render_template("register.html", errors=errors)

    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")
    email = request.form.get("email")

    if not (username or password):
        errors = "Пожалуйста, заполните все поля"
        print(errors)
        return render_template("register.html", errors=errors)

    hashPassword = generate_password_hash(password)
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s", (username,))

    if cur.fetchone() is not None:
        errors = "Пользователь с данным именем уже существует"

        conn.close()
        cur.close()
        
        return render_template("register.html", errors=errors)

    cur.execute("INSERT INTO users (username, password, name, email) VALUES (%s, %s, %s,%s)", (username, hashPassword, name, email))

    conn.commit()
    conn.close()
    cur.close()

    return redirect("/login")

@app.route('/login', methods = ["GET", "POST"])
def login():
    errors = ''

    if request.method == "GET":
        return render_template("login.html", errors=errors)

    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")
    email = request.form.get("email")

    if not (username or password):
        errors = 'Пожалуйста, заполните все поля'
        return render_template("login.html", errors=errors)

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))

    result = cur.fetchone()

    if result is None:
        errors = "Неправильный логин или пароль"
        dbClose(cur, conn)
        return render_template("login.html", errors=errors)

    userID, hashPassword = result

    if check_password_hash(hashPassword, password):
        session['id'] = userID
        session['username'] = username
        dbClose(cur, conn)
        return render_template("base.html", username=username)

    else:
        errors = "Неправильный логин или пароль"
        return render_template("login.html", errors=errors)
    
@app.route("/logout")
def Razlog():
    session.clear()
    return redirect("/login")
    
@app.route("/new_article", methods = ["GET", "POST"])
def createArticle():
    errors =[]

    userID = session.get("id")


    if userID is not None:
        if request.method == "GET":
            return render_template("new_article.html", username=session.get("username"))
        
        if request.method == "POST":
            text_article = request.form.get("text_article")
            title = request.form.get("title_article")

            if len(text_article) == 0:
                errors.append('Заполните текст')
                return render_template("new_article.html", errors=errors, username=session.get("username"))

            conn = dbConnect()
            cur = conn.cursor()

            cur.execute("INSERT INTO advertisement(user_id, title, text) VALUES (%s, %s, %s) RETURNING id", (userID, title, text_article))

            new_article_id = cur.fetchone()[0]
            conn.commit()

            dbClose(cur, conn)

            return redirect(f"/articles/{new_article_id}")

    return redirect("/login")

@app.route("/show")
def showZam():
    userID = session.get("id")
    if userID is not None:
        conn = dbConnect()
        cur = conn.cursor()
        cur.execute("SELECT id, title, text FROM advertisement WHERE user_id = %s", (userID,))
        articles = cur.fetchall()
        conn.commit()
        dbClose(cur, conn)
        return render_template("show.html", articles=articles, username=session.get("username"))

    return redirect("/login")

@app.route('/public_articles')
def publicArticles():
    userID = session.get("id")

    conn = dbConnect()
    cur = conn.cursor()
    cur.execute("SELECT a.id, a.title, a.text, u.username, u.email FROM advertisement a JOIN users u ON a.user_id = u.id")
    articles = cur.fetchall()
    dbClose(cur, conn)
    return render_template('public_articles.html', articles=articles, username=session.get("username"), current_user=userID)



@app.route("/delete_article/<int:article_id>", methods=["POST"])
def deleteArticle(article_id):
    userID = session.get("id")
    if userID is not None:
        conn = dbConnect()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM advertisement WHERE id = %s", (article_id,))
        article_user_id = cur.fetchone()[0]

        if userID != article_user_id:
            return "You are not authorized to delete this article"

        cur.execute("DELETE FROM advertisement WHERE id = %s", (article_id,))
        conn.commit()
        dbClose(cur, conn)

        return redirect("/public_articles")

    return redirect("/login")

@app.route("/delete/<int:userID>", methods=["POST"])
def deleteProfile(userID):
    userID = session.get("id")

    conn = dbConnect()
    cur = conn.cursor()


    cur.execute("DELETE FROM users WHERE id = %s", (userID,))
    conn.commit()
    dbClose(cur, conn)

    return redirect("/login")

@app.route("/edit_article/<int:article_id>", methods=["GET", "POST"])
def editArticle(article_id):
    userID = session.get("id")

    if userID is not None:
        if request.method == "GET":
            conn = dbConnect()
            cur = conn.cursor()
            cur.execute("SELECT user_id, title, text FROM advertisement WHERE id = %s", (article_id,))
            articleData = cur.fetchone()
            dbClose(cur, conn)

            if articleData is not None and articleData[0] == userID:
                return render_template("edit_article.html", article=articleData, username=session.get("username"))

        if request.method == "POST":
            new_title = request.form.get("title")
            new_text = request.form.get("text")

            if len(new_title) == 0 or len(new_text) == 0:
                return "Title and text cannot be empty"

            conn = dbConnect()
            cur = conn.cursor()
            cur.execute("UPDATE advertisement SET title = %s, text = %s WHERE id = %s", (new_title, new_text, article_id))
            conn.commit()
            dbClose(cur, conn)

            return redirect("/show")

    return redirect("/login")


