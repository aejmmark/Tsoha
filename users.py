
from app import app
from db import db

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv, urandom
app.secret_key = getenv("SECRET_KEY")

def login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["csrf_token"] = urandom(16).hex()
            return True
        else:
            return False

def register(username, password, admin):
    """Creates new user
    Sets a negative id to differentiate admins"""
    hash_val = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password, created) VALUES (:username,:password,NOW())"
        db.session.execute(sql, {"username":username, "password":hash_val})
        if admin:
            sql = "UPDATE users SET id=0-id WHERE username=:username"
            db.session.execute(sql, {"username":username})
        db.session.commit()
    except:
        return False
    return login(username,password)

def user_data(id):
    sql = "SELECT u.username, COUNT(DISTINCT l.id), COUNT(DISTINCT t.id), " \
        "COUNT(CASE c.comment WHEN 'DELETE' THEN NULL ELSE 1 END) FROM users u LEFT JOIN comments c " \
            "ON u.id=c.user_id LEFT JOIN threads t ON t.user_id=c.user_id AND t.topic!='DELETE' LEFT JOIN " \
                "likes l ON t.user_id=l.user_id WHERE u.id=:id GROUP BY u.username"
    result = db.session.execute(sql, {"id":id})
    data = result.fetchall()[0]
    return data

def get_user(id):
    result = db.session.execute("SELECT username FROM users WHERE id=:id", {"id":id})
    user = result.fetchone()[0]
    return user

def add_user(username, subject_id):
    sql = "INSERT INTO privileges (subject_id, user_id) VALUES (:subject_id, (SELECT id FROM users WHERE username=:username))"
    try:
        db.session.execute(sql, {"subject_id":subject_id, "username":username})
        db.session.commit()
        return True
    except:
        return False

def remove_user(username, subject_id):
    """removes privileges by setting subject_id to 0"""
    sql = "UPDATE privileges SET subject_id=0 WHERE user_id=(SELECT id FROM users WHERE username=:username) AND subject_id=:subject_id"
    try:
        db.session.execute(sql, {"username":username, "subject_id":subject_id})
        db.session.commit()
        return True
    except:
        return False