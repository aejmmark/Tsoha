from datetime import datetime
from flask import session, request, redirect, render_template

from app import app
import users
import chat

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

@app.route("/new_subject",methods=["GET","POST"])
def new_subject():
    if request.method == "GET":
        return render_template("new_subject.html")
    if request.method == "POST":
        subject = request.form["subject"]
        # validate
        new_id = chat.new_subject(subject)
        if (new_id != 0):
                return redirect("/subject/" + str(new_id))
        return render_template("error.html", message="new_subject error")

@app.route("/new_thread/<int:id>",methods=["GET","POST"])
def new_thread(id):
    if request.method == "GET":
        return render_template("new_thread.html", link=id)
    if request.method == "POST":
        topic = request.form["topic"]
        # validate
        comment = request.form["comment"]
        # validate
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
        # validate
        if chat.new_comment(comment, id, session["user_id"]):
                return redirect("/thread/" + str(id))
        else:
            return render_template("error.html", message="new_comment error")

@app.route("/edit_subject/<int:id>",methods=["GET","POST"])
def edit_subject(id):
    # add check to prevent misuse
    if request.method == "GET":
        return render_template("edit_subject.html", link=id)
    if request.method == "POST":
        delete = request.form["delete"]
        if delete == "DELETE":
            if chat.edit_subject(id, delete, True):
                return redirect("/")
        else:
            edited_subject = request.form["edited_subject"]
            #validate
            secret = request.form["secret"]
            is_secret = secret == "private"
            if chat.edit_subject(id, edited_subject, is_secret):
                return redirect("/")
        return render_template("error.html", message="unable to edit subject")

@app.route("/edit_thread/<int:id>",methods=["GET","POST"])
def edit_thread(id):
    # add check to prevent misuse
    if request.method == "GET":
        return render_template("edit_thread.html", link=id)
    if request.method == "POST":
        delete = request.form["delete"]
        if delete == "DELETE":
            subject_id = chat.edit_thread(id, delete)
            if (subject_id != 0):
                return redirect("/subject/" + str(subject_id))
        else:
            edited_topic = request.form["edited_topic"]
            #validate
            edited_topic = edited_topic + " [EDITED " + str(datetime. now(). strftime("%Y-%m-%d")) +"]"
            subject_id = chat.edit_thread(id, edited_topic)
            if (subject_id != 0):
                    return redirect("/subject/" + str(subject_id))
        return render_template("error.html", message="unable to edit topic")

@app.route("/edit_comment/<int:id>",methods=["GET","POST"])
def edit_comment(id):
    # add check to prevent misuse
    if request.method == "GET":
        return render_template("edit_comment.html", link=id)
    if request.method == "POST":
        delete = request.form["delete"]
        if delete == "DELETE":
            subject_id = chat.edit_comment(id, delete)
            if (subject_id != 0):
                return redirect("/thread/" + str(subject_id))
        else:
            edited_comment = request.form["edited_comment"]
            #validate
            edited_comment = edited_comment + " [EDITED " + str(datetime. now(). strftime("%Y-%m-%d")) +"]"
            thread_id = chat.edit_comment(id, edited_comment)
            if (thread_id != 0):
                    return redirect("/thread/" + str(thread_id))
        return render_template("error.html", message="unable to edit comment")

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
        # validate
        password = request.form["a_password"]
        # validate
        admin = (request.form["usertype"] == "admin")
        if users.register(username,password, admin):
            return redirect("/")
        else:
            return render_template("error.html", message="Username taken")
