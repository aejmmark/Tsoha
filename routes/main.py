from flask import Blueprint, session, request, redirect, render_template, abort, flash
import re
from database import users
from database import chat

main_routes = Blueprint("main_routes", __name__, template_folder="templates")

@main_routes.route("/")
def home():
    user_id = 0
    if session.get("user_id") is not None:
        user = users.get_user(session["user_id"])
        user_id = session["user_id"]
    else:
        user = "account"
    subjects = chat.subjects(user_id)
    return render_template("home.html", user=user, subjects=subjects)

@main_routes.route("/user")
def user():
    data = users.user_data(session["user_id"])
    return render_template("user.html", data=data)

@main_routes.route("/search")
def search():
    keyword = request.args["keyword"]
    results = chat.search(keyword)
    return render_template("search.html", results=results)

@main_routes.route("/subject/<int:id>",methods=["GET","POST"])
def subject(id):
    if request.method == "GET":
        sort = False
        if session.get("thread_sort") is not None:
            sort = True
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        threads = chat.threads(user, id, sort)
        subject = chat.get_subject(id)
        if subject == "DELETE":
            abort(403)
        return render_template("subject.html", subject=subject, link=id, threads=threads)
    if request.method == "POST":
        thread_id = request.form["thread_id"]
        if chat.like_thread(session["user_id"], thread_id):
            return redirect("/subject/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/subject/" + str(id))

@main_routes.route("/thread/<int:id>",methods=["GET","POST"])
def thread(id):
    if request.method == "GET":
        sort = False
        if session.get("comment_sort") is not None:
            sort = True
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        comments = chat.comments(user, id, sort)
        topic = chat.get_topic(id)
        if topic == "DELETE":
            abort(403)
        return render_template("thread.html", topic=topic[1], link=id, comments=comments, back=("/subject/" + str(topic[0])))
    if request.method == "POST":
        comment_id = request.form["comment_id"]
        if chat.like_comment(session["user_id"], comment_id):
            return redirect("/thread/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/thread/" + str(id))

@main_routes.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username,password):
            flash("login succesful!")
            return redirect("/")
        else:
            flash("wrong username or password")
            return redirect("/login")

@main_routes.route("/logout")
def logout():
    del session["user_id"]
    del session["csrf_token"]
    flash("logged out")
    return redirect("/")

@main_routes.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        if (request.form["a_password"] != request.form["b_password"]):
            flash("passwords do not match")
            return redirect("/register")
        username = request.form["username"]
        password = request.form["a_password"]
        if len(username) > 12 or len(username) < 3 or len(password) > 16 or len(password) < 8 or bool(re.search(r'\W', username)):
            flash("invalid username or password")
            return redirect("/register")
        admin = (request.form["usertype"] == "admin")
        if users.register(username,password, admin):
            flash("new user created")
            return redirect("/")
        else:
            flash("username taken")
            return redirect("/register")
