from flask import Blueprint, session, request, redirect, render_template, abort, flash
import re
from database import users

users_routes = Blueprint("users_routes", __name__, template_folder="templates")

@users_routes.route("/user")
def user():
    data = users.user_data(session["user_id"])
    return render_template("user.html", data=data)


@users_routes.route("/login",methods=["GET","POST"])
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

@users_routes.route("/logout")
def logout():
    del session["user_id"]
    del session["csrf_token"]
    flash("logged out")
    return redirect("/")

@users_routes.route("/register",methods=["GET","POST"])
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

@users_routes.route("/add_user/<int:id>", methods=["POST"])
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

@users_routes.route("/remove_user/<int:id>", methods=["POST"])
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
