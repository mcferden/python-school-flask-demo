import sqlite3

from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask.views import MethodView
from werkzeug.security import generate_password_hash

from database import db


bp = Blueprint('users', __name__)


class UsersView(MethodView):
    def get(self):
        con = db.connection
        cur = con.execute(
            'SELECT id, username '
            'FROM user'
        )
        rows = cur.fetchall()
        return jsonify([dict(row) for row in rows])

    def post(self):
        request_json = request.json
        username = request_json.get('username')
        password = request_json.get('password')

        if not username or not password:
            return '', 400

        password_hash = generate_password_hash(password)

        con = db.connection
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


class UserView(MethodView):
    def get(self, user_id):
        con = db.connection
        cur = con.execute(
            'SELECT id, username '
            'FROM user '
            'WHERE id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404
        return jsonify(dict(user))

    def patch(self, user_id):
        request_json = request.json
        username = request_json.get('username')
        if not username:
            return '', 400

        con = db.connection

        cur = con.execute(
            'SELECT id, username '
            'FROM user '
            'WHERE id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404

        con.execute(
            'UPDATE user '
            'SET username = ? '
            'WHERE id = ?',
            (username, user_id),
        )
        con.commit()
        return '', 200


bp.add_url_rule('', view_func=UsersView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UserView.as_view('user'))
