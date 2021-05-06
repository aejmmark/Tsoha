from app import app
from database.db import db

def search(keyword):
    sql = "SELECT t.id, c.comment, c.posted, t.topic FROM comments c, threads t WHERE t.id=c.thread_id " \
        "AND (c.comment LIKE :keyword OR t.topic LIKE :keyword) AND t.topic!='DELETE' ORDER BY c.posted DESC"
    result = db.session.execute(sql, {"keyword":"%"+keyword+"%"})
    results = result.fetchall()
    return results

def subjects(user_id):
    sql = "SELECT s.id, s.subject, COUNT(DISTINCT t.id), COUNT(CASE WHEN c.comment='DELETE' OR c.comment IS NULL THEN NULL ELSE 1 END), " \
        "MAX(c.posted), s.secret, COUNT(DISTINCT p.id) FROM subjects s LEFT JOIN threads t ON s.id=t.subject_id AND t.topic!='DELETE' LEFT JOIN " \
            "comments c ON t.id=c.thread_id LEFT JOIN privileges p ON p.subject_id=s.id AND p.user_id=:user_id WHERE s.subject!='DELETE' GROUP BY s.id ORDER BY s.id"
    result = db.session.execute(sql, {"user_id":user_id})
    subjects = result.fetchall()
    return subjects

def threads(user_id, subject_id, sort):
    sql = "SELECT MIN(s.subject), t.id, MIN(t.topic), COUNT(DISTINCT l.id), COUNT(CASE WHEN c.comment='DELETE' " \
        "OR c.comment IS NULL THEN NULL ELSE 1 END) / COALESCE(NULLIF(COUNT(DISTINCT l.id),0), 1), MAX(c.posted), (SELECT COUNT(id) FROM likes WHERE user_id=:user_id " \
            "AND thread_id=t.id), MIN(t.user_id) FROM subjects s, comments c, threads t LEFT JOIN likes l ON t.id=l.thread_id " \
                "WHERE t.id=c.thread_id AND t.subject_id=:subject_id AND s.id=t.subject_id AND t.topic!='DELETE' GROUP BY t.id "
    if sort:
        sql += "ORDER BY COUNT(DISTINCT l.id) DESC"
    else:
        sql += "ORDER BY MIN(c.posted) DESC"
    result = db.session.execute(sql, {"subject_id":subject_id, "user_id":user_id})
    threads = result.fetchall()
    return threads

def comments(user_id, thread_id, sort):
    sql = "SELECT MIN(t.topic), MIN(c.id), MIN(c.comment), MIN(u.username), COUNT(l.id), MIN(c.posted), " \
        "(SELECT COUNT(id) FROM likes WHERE user_id=:user_id AND comment_id=MIN(c.id)), MIN(u.id) FROM threads t, users u, comments c" \
            " LEFT JOIN likes l ON c.id=l.comment_id WHERE c.user_id=u.id AND c.thread_id=t.id AND t.id=:thread_id AND c.comment!='DELETE' " \
                "GROUP BY c.id "
    if sort:
        sql += "ORDER BY COUNT(DISTINCT l.id) DESC"
    else:
        sql += "ORDER BY MIN(c.posted)"
    result = db.session.execute(sql, {"thread_id":thread_id, "user_id":user_id})
    comments = result.fetchall()
    return comments

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

def like_comment(user_id, comment):
    sql = "INSERT INTO likes (user_id, comment_id) VALUES (:user_id, :comment)"
    try:
        db.session.execute(sql, {"user_id":user_id, "comment":comment})
        db.session.commit()
        return True
    except:
        return False

def like_thread(user_id, thread_id):
    sql = "INSERT INTO likes (user_id, thread_id) VALUES (:user_id, :thread_id)"
    try:
        db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id})
        db.session.commit()
        return True
    except:
        return False

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

def get_subject(subject_id):
    result = db.session.execute("SELECT subject FROM subjects WHERE id=:subject_id", {"subject_id":subject_id})
    subject = result.fetchone()[0]
    return subject

def get_topic(thread_id):
    result = db.session.execute("SELECT subject_id, topic FROM threads WHERE id=:thread_id", {"thread_id":thread_id})
    topic = result.fetchone()
    return topic

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