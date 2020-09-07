import os
import hashlib
import werkzeug
import requests


#hashing tutorial taken from https://pythonprogramming.net/password-hashing-flask-tutorial/
salt = "salt"

from flask import Flask, session, render_template, request, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
username_error_length_short = "Username must be longer than 3 characters."
username_error_length_long = "Username must be shorter than 21 characters."
username_error_exists = "Account with username already exists."
username_error_not_exists = "Account with username does not exist."
password_error_length_short = "Password must be longer than 3 characters."
password_error_length_long = "Password must be shorter than 21 characters."
password_error_incorrect = "Incorrect password."
search_nothing = "Search empty."
already_submitted_review = "Cannot submit more than one review for a book."
review_nothing = "Review cannot be empty."
rate_nothing = "A rating must be selected."

min_length = 3
max_length = 20

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def login():
    session["username"] = ""
    return render_template("login.html", errormessage='')

@app.route("/home", methods=["POST", "GET"])
def home():
    if session.get("username") == "":
        username = request.form.get("username")
        password = request.form.get("password")

        if "createacc" in request.form:
            if db.execute("SELECT * FROM users WHERE fstrusername = :username", {"username": username}).rowcount > 0:
                return render_template("login.html", errormessage=username_error_exists)
            if len(username) <= min_length:
                return render_template("login.html", errormessage=username_error_length_short)
            if len(password) <= min_length:
                return render_template("login.html", errormessage=password_error_length_short)
            if len(username) > max_length:
                return render_template("login.html", errormessage=username_error_length_long)
            if len(password) > max_length:
                return render_template("login.html", errormessage=password_error_length_long)

            hashed_password = password+salt
            h = hashlib.md5(hashed_password.encode())

            db.execute("INSERT INTO users (fstrusername, fstrhashedpassword, fintuserid, fstremail) VALUES (:username, :password, :userid, :email)", {"username": username, "password": h.hexdigest()[:20], "userid": 0, "email": ""})
            db.commit()

            if session.get("username") == "":
                session["username"] = username
            return render_template("home.html", user=username, errormessage="")

        if "login" in request.form:
            if len(username) <= min_length:
                return render_template("login.html", errormessage=username_error_length_short)
            if len(password) <= min_length:
                return render_template("login.html", errormessage=password_error_length_short)
            if len(username) > max_length:
                return render_template("login.html", errormessage=username_error_length_long)
            if len(password) > max_length:
                return render_template("login.html", errormessage=password_error_length_long)
            if db.execute("SELECT * FROM users WHERE fstrusername = :username", {"username": username}).rowcount == 0:
                return render_template("login.html", errormessage=username_error_not_exists)

            hashed_password = password+salt
            h = hashlib.md5(hashed_password.encode())
            if db.execute("SELECT * FROM users WHERE fstrusername = :username AND fstrhashedpassword = :hashedpassword ", {"username": username, "hashedpassword": h.hexdigest()[:20]}).rowcount == 0:
                return render_template("login.html", errormessage=password_error_incorrect)
            if session.get("username") == '':
                session["username"] = username
            return render_template("home.html", user=username, errormessage="")
    if session.get("username") != "":
        return render_template("home.html", user=session.get("username"), errormessage="")

    

@app.route("/search", methods=["POST"])
def search():
    if session.get("username") == "":
        return render_template("login.html")
    if "search" not in request.form:
        abort(404)
    if len(request.form.get("search_criteria")) == 0:
        return render_template("home.html", user=session["username"], errormessage=search_nothing)

    search = '%'+request.form.get("search_criteria")+'%'

    books  = db.execute("SELECT fstrtitle, fstrauthor, fi16year, fstrisbn FROM books WHERE fstrtitle ILIKE :title UNION ALL SELECT fstrtitle, fstrauthor, fi16year, fstrisbn FROM books WHERE fstrauthor ILIKE :author UNION ALL SELECT fstrtitle, fstrauthor, fi16year, fstrisbn FROM books WHERE fstrisbn ILIKE :isbn",
                              {"title": search, "author": search, "isbn": search}).fetchall()
    return render_template("search.html", books=books)

@app.route("/api/<string:isbn>")
def isbn_api(isbn):
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "PMKaLOm3ScRMRKSSJVsMpA", "isbns": isbn})
        book  = db.execute("SELECT fstrtitle, fstrauthor, fi16year FROM books WHERE fstrisbn = :isbn",
                              {"isbn": isbn}).fetchall()
        if len(book) == 0:
            raise Exception('No book with isbn found')
        return jsonify(title= book[0][0], author= book[0][1], year= book[0][2], isbn= isbn, review_count=res.json()["books"][0]["reviews_count"], average_score= res.json()["books"][0]["average_rating"])
    except:
        abort(404)

@app.route("/book", methods=["GET","POST"])
def book():
    if session.get("username") == "":
        return render_template("login.html")
    error_message = ''
    book_name = request.args.get('book_name', '')
    book  = db.execute("SELECT fstrisbn, fstrauthor, fi16year FROM books WHERE fstrtitle = :title",
                              {"title": book_name}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "PMKaLOm3ScRMRKSSJVsMpA", "isbns": book[0][0]})
    
    
    if "submit" in request.form:
        if "rate" not in request.form:
            error_message = rate_nothing
        elif "book_review" not in request.form:
            print(request.form)
            error_message = review_nothing
        else:
            rating = int(request.form.get('rate'))
            self_reviews  = db.execute("SELECT fstruser, fi16score, fstrreview FROM reviews WHERE fstrbook = :title AND fstruser = :user",
                                  {"title": book_name, "user": session["username"]}).fetchall()
            print(self_reviews)
            if len(self_reviews) != 0:
                error_message = already_submitted_review
            else:
                db.execute("INSERT INTO reviews (fstruser, fi16score, fstrbook, fstrreview) VALUES (:user, :score, :book, :review)", {"user": session["username"], "score": rating, "book": book_name, "review": request.form.get('book_review')})
                db.commit()

    
    reviews  = db.execute("SELECT fstruser, fi16score, fstrreview FROM reviews WHERE fstrBook = :title",
                              {"title": book_name}).fetchall()

    if len(book) == 0:
        abort(404)
    return render_template("book.html", title=book_name, author= book[0][1], year= book[0][2], isbn= book[0][0], num_rating=res.json()["books"][0]["reviews_count"], avg_rating= res.json()["books"][0]["average_rating"], reviews = reviews, submit_error_message = error_message)

 