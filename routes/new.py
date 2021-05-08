from flask import Blueprint, session, request, redirect, render_template, abort, flash
from datetime import datetime
from database import edit
from database.main import subject_secret, subject_check_privilege, \
    thread_secret, thread_check_privilege

new_routes = Blueprint("new_routes", __name__, template_folder="templates")

@new_routes.route("/new_subject",methods=["GET","POST"])
def new_subject():
    if session["user_id"] > 0:
        abort(403)
    if request.method == "GET":
        return render_template("new_subject.html")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        subject = request.form["subject"]
        if len(subject) > 60 or len(subject) < 3:
            flash("invalid subject")
            return redirect("/new_subject")
        secret = request.form["secret"]
        is_secret = secret == "private"
        new_id = edit.new_subject(subject, is_secret)
        if (new_id != 0):
                flash("subject created")
                return redirect("/subject/" + str(new_id))
        flash("unexpected error, try again")
        return redirect("/new_subject")

@new_routes.route("/new_thread/<int:id>",methods=["GET","POST"])
def new_thread(id):
    if subject_secret(id):
            if session.get("user_id") is None or not subject_check_privilege(session["user_id"], id):
                abort(403)
    if request.method == "GET":
        return render_template("new_thread.html", link=id, back=("/subject/" + str(id)))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        topic = request.form["topic"]
        comment = request.form["comment"]
        if len(topic) > 60 or len(topic) < 3 or len(comment) > 500 or len(comment) < 3:
            flash("invalid topic or comment")
            return redirect("/new_thread/" + str(id))
        new_id = edit.new_thread(comment, id, session["user_id"], topic)
        if (new_id != 0):
                flash("topic posted")
                return redirect("/thread/" + str(new_id))
        flash("unexpected error, try again")
        return redirect("/new_thread/" + str(id))

@new_routes.route("/new_comment/<int:id>",methods=["GET","POST"])
def new_comment(id):
    if thread_secret(id):
            if session.get("user_id") is None or not thread_check_privilege(session["user_id"], id):
                abort(403)
    if request.method == "GET":
        return render_template("new_comment.html", link=id, back=("/thread/" + str(id)))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        comment = request.form["comment"]
        if len(comment) > 500 or len(comment) < 3:
            flash("invalid comment")
            return redirect("/new_comment/" + str(id))
        if edit.new_comment(comment, id, session["user_id"]):
                flash("comment posted")
                return redirect("/thread/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/new_comment/" + str(id))
