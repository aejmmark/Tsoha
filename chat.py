
from app import app
from db import db

def subjects():
    sql = "SELECT s.id, s.subject, COUNT(DISTINCT t.id), COUNT(c.id), MAX(c.posted) FROM subjects s LEFT JOIN threads t ON s.id=t.subject_id " \
        "LEFT JOIN comments c ON t.id=c.thread_id GROUP BY s.id ORDER BY s.id"
    result = db.session.execute(sql)
    subjects = result.fetchall()
    return subjects

def threads(user, subject):
    sql = "SELECT MIN(s.subject), t.id, MIN(t.topic), COUNT(DISTINCT l.id), COUNT(DISTINCT c.id), MAX(c.posted), " \
        "(SELECT COUNT(id) FROM likes WHERE user_id=:user_id AND thread_id=t.id) " \
            "FROM subjects s, comments c, threads t LEFT JOIN likes l ON t.id=l.thread_id " \
                "WHERE t.id=c.thread_id AND t.subject_id=:subject AND s.id=t.subject_id GROUP BY t.id ORDER BY MIN(c.posted) DESC"
    result = db.session.execute(sql, {"subject":subject, "user_id":user})
    threads = result.fetchall()
    return threads

def comments(user, thread):
    sql = "SELECT MIN(t.topic), MIN(c.id), MIN(c.comment), MIN(u.username), COUNT(l.id), MIN(c.posted), " \
        "(SELECT COUNT(id) FROM likes WHERE user_id=:user_id AND comment_id=MIN(c.id)) FROM threads t, users u, comments c" \
            " LEFT JOIN likes l ON c.id=l.comment_id WHERE c.user_id=u.id AND c.thread_id=t.id AND t.id=:thread GROUP BY c.id ORDER BY MIN(c.posted)"
    result = db.session.execute(sql, {"thread":thread, "user_id":user})
    comments = result.fetchall()
    return comments

def new_comment(comment, thread, user_id):
    sql = "INSERT INTO comments (thread_id, user_id, comment, posted) VALUES (:thread,:user_id,:comment,NOW())"
    try:
        db.session.execute(sql, {"thread":thread, "user_id":user_id, "comment":comment})
        db.session.commit()
        return True
    except:
        return False

def new_thread(comment, subject, user_id, topic):
    sql_threads = "INSERT INTO threads (subject_id, user_id, topic, created) VALUES (:subject,:user_id,:topic,NOW()) RETURNING id"
    sql_comments = "INSERT INTO comments (thread_id, user_id, comment, posted) VALUES (:thread,:user_id,:comment,NOW())"
    try:
        result = db.session.execute(sql_threads, {"subject":subject, "user_id":user_id, "topic":topic})
        new_id = result.fetchone()[0]
        db.session.execute(sql_comments, {"thread":new_id, "user_id":user_id, "comment":comment})
        db.session.commit()
        return new_id
    except:
        return 0

def like_comment(user, comment):
    sql = "INSERT INTO likes (user_id, comment_id) VALUES (:user, :comment)"
    try:
        db.session.execute(sql, {"user":user, "comment":comment})
        db.session.commit()
        return True
    except:
        return False

def like_thread(user, thread):
    sql = "INSERT INTO likes (user_id, thread_id) VALUES (:user, :thread)"
    try:
        db.session.execute(sql, {"user":user, "thread":thread})
        db.session.commit()
        return True
    except:
        return False

def search(keyword):
    sql = "SELECT t.id, c.comment, c.posted, t.topic FROM comments c, threads t WHERE t.id=c.thread_id AND (c.comment LIKE :keyword OR t.topic LIKE :keyword) ORDER BY c.posted DESC"
    result = db.session.execute(sql, {"keyword":"%"+keyword+"%"})
    results = result.fetchall()
    return results

def get_user(id):
    result = db.session.execute("SELECT username FROM users WHERE id=:id", {"id":id})
    user = result.fetchone()[0]
    return user

def get_subject(id):
    result = db.session.execute("SELECT subject FROM subjects WHERE id=:id", {"id":id})
    subject = result.fetchone()[0]
    return subject

def get_topic(id):
    result = db.session.execute("SELECT topic FROM threads WHERE id=:id", {"id":id})
    topic = result.fetchone()[0]
    return topic
