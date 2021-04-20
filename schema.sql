
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    created TIMESTAMP
);

CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    secret BOOLEAN,
    subject TEXT
);

INSERT INTO subjects (id, secret, subject) VALUES (0, True, 'DELETE');

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects,
    user_id INTEGER REFERENCES users,
    topic TEXT,
    created TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads,
    user_id  INTEGER REFERENCES users,
    comment TEXT,
    posted TIMESTAMP
);

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    thread_id INTEGER REFERENCES threads,
    comment_id INTEGER REFERENCES comments
);

CREATE TABLE privileges (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects,
    user_id INTEGER REFERENCES users
);