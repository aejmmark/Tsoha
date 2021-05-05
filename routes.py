from datetime import datetime
import re
from flask import session, request, redirect, render_template, abort, flash

from app import app
import users
import chat

@app.route("/")
def home():
    user_id = 0
    if session.get("user_id") is not None:
        user = users.get_user(session["user_id"])
        user_id = session["user_id"]
    else:
        user = "account"
    subjects = chat.subjects(user_id)
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

@app.route("/thread/<int:id>",methods=["GET","POST"])
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

@app.route("/sort_threads/<int:id>", methods=["POST"])
def sort_threads(id):
    if session.get("thread_sort") is not None:
        del session["thread_sort"]
    else:    
        session["thread_sort"] = "likes"
    return redirect("/subject/" + str(id))

@app.route("/sort_comments/<int:id>", methods=["POST"])
def sort_comments(id):
    if session.get("comment_sort") is not None:
        del session["comment_sort"]
    else:    
        session["comment_sort"] = "likes"
    return redirect("/thread/" + str(id))

@app.route("/new_subject",methods=["GET","POST"])
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
        new_id = chat.new_subject(subject, is_secret)
        if (new_id != 0):
                flash("subject created")
                return redirect("/subject/" + str(new_id))
        flash("unexpected error, try again")
        return redirect("/new_subject")

@app.route("/new_thread/<int:id>",methods=["GET","POST"])
def new_thread(id):
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
        new_id = chat.new_thread(comment, id, session["user_id"], topic)
        if (new_id != 0):
                flash("topic posted")
                return redirect("/thread/" + str(new_id))
        flash("unexpected error, try again")
        return redirect("/new_thread/" + str(id))

@app.route("/new_comment/<int:id>",methods=["GET","POST"])
def new_comment(id):
    if request.method == "GET":
        return render_template("new_comment.html", link=id, back=("/thread/" + str(id)))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        comment = request.form["comment"]
        if len(comment) > 500 or len(comment) < 3:
            flash("invalid comment")
            return redirect("/new_comment/" + str(id))
        if chat.new_comment(comment, id, session["user_id"]):
                flash("comment posted")
                return redirect("/thread/" + str(id))
        else:
            flash("unexpected error, try again")
            return redirect("/new_comment/" + str(id))

@app.route("/edit_subject/<int:id>",methods=["GET","POST"])
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

@app.route("/edit_thread/<int:id>",methods=["GET","POST"])
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

@app.route("/edit_comment/<int:id>",methods=["GET","POST"])
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

@app.route("/add_user/<int:id>", methods=["POST"])
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

@app.route("/remove_user/<int:id>", methods=["POST"])
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

@app.route("/login",methods=["GET","POST"])
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

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["csrf_token"]
    flash("logged out")
    return redirect("/")

@app.route("/register",methods=["GET","POST"])
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
