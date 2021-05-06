from app import app
from database.db import db

def new_comment(comment, thread_id, user_id):
    sql = "INSERT INTO comments (thread_id, user_id, comment, posted) VALUES (:thread_id,:user_id,:comment,NOW())"
    try:
        db.session.execute(sql, {"thread_id":thread_id, "user_id":user_id, "comment":comment})
        db.session.commit()
        return True
    except:
        return False

def new_thread(comment, subject_id, user_id, topic):
    sql_threads = "INSERT INTO threads (subject_id, user_id, topic, created) VALUES (:subject_id,:user_id,:topic,NOW()) RETURNING id"
    sql_comments = "INSERT INTO comments (thread_id, user_id, comment, posted) VALUES (:thread_id,:user_id,:comment,NOW())"
    try:
        result = db.session.execute(sql_threads, {"subject_id":subject_id, "user_id":user_id, "topic":topic})
        new_id = result.fetchone()[0]
        db.session.execute(sql_comments, {"thread_id":new_id, "user_id":user_id, "comment":comment})
        db.session.commit()
        return new_id
    except:
        return 0

def new_subject(subject, secret):
    sql = "INSERT INTO subjects (secret, subject) VALUES (:secret, :subject) RETURNING id"
    try:
        result = db.session.execute(sql, {"secret":secret, "subject":subject})
        new_id = result.fetchone()[0]
        db.session.commit()
        return new_id
    except:
        return 0
def edit_subject(subject_id, new_subject, secret):
    sql = "UPDATE subjects SET subject=:new_subject, secret=:secret WHERE id=:subject_id"
    try:
        db.session.execute(sql, {"new_subject":new_subject, "secret":secret, "subject_id":subject_id})
        db.session.commit()
        return True
    except:
        return False

def edit_thread(thread_id, new_topic):
    sql = "UPDATE threads SET topic=:new_topic WHERE id=:thread_id RETURNING subject_id"
    try:
        result = db.session.execute(sql, {"new_topic":new_topic, "thread_id":thread_id})
        subject_id = result.fetchone()[0]
        db.session.commit()
        return subject_id
    except:
        return 0

def edit_comment(comment_id, new_comment):
    sql = "UPDATE comments SET comment=:new_comment WHERE id=:comment_id RETURNING thread_id"
    try:
        result = db.session.execute(sql, {"new_comment":new_comment, "comment_id":comment_id})
        thread_id = result.fetchone()[0]
        db.session.commit()
        return thread_id
    except:
        return 0

def get_comment_thread_id(comment_id):
    result = db.session.execute("SELECT thread_id FROM comments WHERE id=:comment_id", {"comment_id":comment_id})
    thread_id = result.fetchone()[0]
    return thread_id

def get_thread_subject_id(thread_id):
    result = db.session.execute("SELECT subject_id FROM threads WHERE id=:thread_id", {"thread_id":thread_id})
    subject_id = result.fetchone()[0]
    return subject_id

def get_topic_poster(thread_id):
    result = db.session.execute("SELECT user_id FROM threads WHERE id=:thread_id", {"thread_id":thread_id})
    user_id = result.fetchone()[0]
    return user_id

def get_comment_poster(comment_id):
    result = db.session.execute("SELECT user_id FROM comments WHERE id=:comment_id", {"comment_id":comment_id})
    user_id = result.fetchone()[0]
    return user_id
