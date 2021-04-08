
from app import app
import users
import chat

from flask import session, request, redirect, render_template

@app.route("/")
def home():
    subjects = chat.subjects()
    if session.get("user_id") is not None:
        user = chat.get_user(session["user_id"])
    else:
        user = "account"
    return render_template("home.html", user=user, subjects=subjects)

@app.route("/user")
def user():
    data = users.user_data(session["user_id"])
    return render_template("user.html", data=data)

@app.route("/search")
def search():
    keyword = request.args["keyword"]
    results = chat.search(keyword)
    return render_template("search.html", results=results)

@app.route("/subject/<int:id>",methods=["GET","POST"])
def subject(id):
    if request.method == "GET":
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        threads = chat.threads(user, id)
        subject = chat.get_subject(id)
        return render_template("subject.html", subject=subject, link=id, threads=threads)
    if request.method == "POST":
        thread_id = request.form["thread_id"]
        if chat.like_thread(session["user_id"], thread_id):
            return redirect("/subject/" + str(id))
        else:
            return render_template("error.html", message="like_thread error")

@app.route("/thread/<int:id>",methods=["GET","POST"])
def thread(id):
    if request.method == "GET":
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        comments = chat.comments(user, id)
        topic = chat.get_topic(id)
        return render_template("thread.html", topic=topic, link=id, comments=comments)
    if request.method == "POST":
        comment_id = request.form["comment_id"]
        if chat.like_comment(session["user_id"], comment_id):
            return redirect("/thread/" + str(id))
        else:
            return render_template("error.html", message="like_comment error")

@app.route("/new_thread/<int:id>",methods=["GET","POST"])
def new_thread(id):
    if request.method == "GET":
        return render_template("new_thread.html", link=id)
    if request.method == "POST":
        topic = request.form["topic"]
        comment = request.form["comment"]
        new_id = chat.new_thread(comment, id, session["user_id"], topic)
        if (new_id != 0):
                return redirect("/thread/" + str(new_id))
        return render_template("error.html", message="new_thread error")

@app.route("/new_comment/<int:id>",methods=["GET","POST"])
def new_comment(id):
    if request.method == "GET":
        return render_template("new_comment.html", link=id)
    if request.method == "POST":
        comment = request.form["comment"]
        if chat.new_comment(comment, id, session["user_id"]):
                return redirect("/thread/" + str(id))
        else:
            return render_template("error.html", message="new_comment error")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username,password):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong username or password")

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        if (request.form["a_password"] != request.form["b_password"]):
            return render_template("error.html", message="Passwords do not match")
        username = request.form["username"]
        password = request.form["a_password"]
        admin = (request.form["usertype"] == "admin")
        if users.register(username,password, admin):
            return redirect("/")
        else:
            return render_template("error.html", message="Username taken")

