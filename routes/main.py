from flask import Blueprint, session, request, redirect, render_template, abort, flash
import re
from database.users import get_user
from database import main

main_routes = Blueprint("main_routes", __name__, template_folder="templates")

@main_routes.route("/")
def home():
    user_id = 0
    if session.get("user_id") is not None:
        user = get_user(session["user_id"])
        user_id = session["user_id"]
    else:
        user = "account"
    subjects = main.subjects(user_id)
    return render_template("home.html", user=user, subjects=subjects)

@main_routes.route("/search")
def search():
    keyword = request.args["keyword"]
    results = main.search(keyword)
    return render_template("search.html", results=results)

@main_routes.route("/subject/<int:id>",methods=["GET","POST"])
def subject(id):
    if request.method == "GET":
        if main.subject_secret(id):
            if session.get("user_id") is None or not main.subject_check_privilege(session["user_id"], id):
                abort(403)
        sort = False
        if session.get("thread_sort") is not None:
            sort = True
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        threads = main.threads(user, id, sort)
        subject = main.get_subject(id)
        if subject == "DELETE":
            abort(403)
        return render_template("subject.html", subject=subject, link=id, threads=threads)
    if request.method == "POST":
        thread_id = request.form["thread_id"]
        if main.like_thread(session["user_id"], thread_id):
            return redirect("/subject/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/subject/" + str(id))

@main_routes.route("/thread/<int:id>",methods=["GET","POST"])
def thread(id):
    if request.method == "GET":
        if main.thread_secret(id):
            if session.get("user_id") is None or not main.thread_check_privilege(session["user_id"], id):
                abort(403)
        sort = False
        if session.get("comment_sort") is not None:
            sort = True
        user = 0
        if session.get("user_id") is not None:
            user = session["user_id"]
        comments = main.comments(user, id, sort)
        topic = main.get_topic(id)
        if topic == "DELETE":
            abort(403)
        return render_template("thread.html", topic=topic[1], link=id, comments=comments, back=("/subject/" + str(topic[0])))
    if request.method == "POST":
        comment_id = request.form["comment_id"]
        if main.like_comment(session["user_id"], comment_id):
            return redirect("/thread/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/thread/" + str(id))
