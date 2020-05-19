import sqlite3

from flask import (
    Flask,
    jsonify,
    request,
    session,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from db import (
    close_db,
    get_db,
)


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/ads')
def get_ads():
    user_id = session.get('user_id')
    if user_id is None:
        return '', 403

    con = get_db()
    cur = con.execute(
        'SELECT * '
        'FROM ad '
        'WHERE user_id = ?',
        (user_id,),
    )
    result = cur.fetchall()
    return jsonify([dict(row) for row in result])


@app.route('/login', methods=['POST'])
def login():
    request_json = request.json
    username = request_json.get('username')
    password = request_json.get('password')

    if not username or not password:
        return '', 400

    con = get_db()
    cur = con.execute(
        'SELECT * '
        'FROM user '
        'WHERE username = ?',
        (username,),
    )
    user = cur.fetchone()

    if user is None:
        return '', 403

    if not check_password_hash(user['password'], password):
        return '', 403

    session['user_id'] = user['id']
    return '', 200


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return '', 200


@app.route('/register', methods=['POST'])
def register():
    request_json = request.json
    username = request_json.get('username')
    password = request_json.get('password')

    if not username or not password:
        return '', 400

    password_hash = generate_password_hash(password)

    con = get_db()
    try:
        con.execute(
            'INSERT INTO user (username, password) '
            'VALUES (?, ?)',
            (username, password_hash),
        )
        con.commit()
    except sqlite3.IntegrityError:
        return '', 409

    return '', 201
