from flask import Blueprint, session, request, redirect, render_template, abort, flash
from datetime import datetime
from database import users
from database import chat

edit_routes = Blueprint("edit_routes", __name__, template_folder="templates")

@edit_routes.route("/sort_threads/<int:id>", methods=["POST"])
def sort_threads(id):
    if session.get("thread_sort") is not None:
        del session["thread_sort"]
    else:    
        session["thread_sort"] = "likes"
    return redirect("/subject/" + str(id))

@edit_routes.route("/sort_comments/<int:id>", methods=["POST"])
def sort_comments(id):
    if session.get("comment_sort") is not None:
        del session["comment_sort"]
    else:    
        session["comment_sort"] = "likes"
    return redirect("/thread/" + str(id))

@edit_routes.route("/edit_subject/<int:id>",methods=["GET","POST"])
def edit_subject(id):
    if session["user_id"] > 0:
        abort(403)
    if request.method == "GET":
        return render_template("edit_subject.html", link=id)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        delete = request.form["delete"]
        if delete == "DELETE":
            if chat.edit_subject(id, delete, True):
                flash("subject deleted")
                return redirect("/")
        else:
            edited_subject = request.form["edited_subject"]
            if len(edited_subject) > 60 or len(edit_subject) < 3:
                flash("invalid subject")
                return redirect("/edit_subject/" + str(id))
            secret = request.form["secret"]
            is_secret = secret == "private"
            if chat.edit_subject(id, edited_subject, is_secret):
                flash("subject edited")
                return redirect("/")
        flash("unable to edit subject")
        return redirect("/edit_subject/" + str(id))

@edit_routes.route("/edit_thread/<int:id>",methods=["GET","POST"])
def edit_thread(id):
    if session["user_id"] != chat.get_topic_poster(id) and session["user_id"] > 0:
        abort(403)
    if request.method == "GET":
        subject_id = chat.get_thread_subject_id(id)
        return render_template("edit_thread.html", link=id, back=("/subject/" + str(subject_id)))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        delete = request.form["delete"]
        if delete == "DELETE":
            subject_id = chat.edit_thread(id, delete)
            if (subject_id != 0):
                flash("thread deleted")
                return redirect("/subject/" + str(subject_id))
        else:
            edited_topic = request.form["edited_topic"]
            if len(edited_topic) > 60 or len(edited_topic) < 3:
                flash("invalid topic")
                return redirect("/edit_thread/" + str(id))
            edited_topic = edited_topic + "\n[EDITED " + str(datetime. now(). strftime("%Y-%m-%d")) +"]"
            subject_id = chat.edit_thread(id, edited_topic)
            if (subject_id != 0):
                    flash("topic edited")
                    return redirect("/subject/" + str(subject_id))
        flash("unable to edit topic")
        return redirect("/edit_thread/" + str(id))

@edit_routes.route("/edit_comment/<int:id>",methods=["GET","POST"])
def edit_comment(id):
    if session["user_id"] != chat.get_comment_poster(id) and session["user_id"] > 0:
        abort(403)
    if request.method == "GET":
        thread_id = chat.get_comment_thread_id(id)
        return render_template("edit_comment.html", link=id, back=("/thread/" + str(thread_id)))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        delete = request.form["delete"]
        if delete == "DELETE":
            subject_id = chat.edit_comment(id, delete)
            if (subject_id != 0):
                flash("comment deleted")
                return redirect("/thread/" + str(subject_id))
        else:
            edited_comment = request.form["edited_comment"]
            if len(edited_comment) > 500 or len(edited_comment) < 3:
                flash("invalid comment")
                return redirect("/edit_comment/" + str(id))
            edited_comment = edited_comment + "\n[EDITED " + str(datetime. now(). strftime("%Y-%m-%d")) +"]"
            thread_id = chat.edit_comment(id, edited_comment)
            if (thread_id != 0):
                    flash("comment edited")
                    return redirect("/thread/" + str(thread_id))
        flash("unable to edit comment")
        return redirect("/edit_comment/" + str(id))

@edit_routes.route("/add_user/<int:id>", methods=["POST"])
def add_user(id):
    if session["user_id"] > 0:
        abort(403)
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user = request.form["add_user"]
    if users.add_user(user, id):
        flash("privileges added")
        return redirect("/")
    else:
        flash("unable to add privileges")
        return redirect("/edit_subject/" + str(id))

@edit_routes.route("/remove_user/<int:id>", methods=["POST"])
def remove_user(id):
    if session["user_id"] > 0:
        abort(403)
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user = request.form["remove_user"]
    if users.remove_user(user, id):
        flash("privileges removed")
        return redirect("/")
    else:
        flash("unable to remove privileges")
        return redirect("/edit_subject/" + str(id))
