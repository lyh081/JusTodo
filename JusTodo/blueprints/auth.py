from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from JusTodo.extensions import db
from JusTodo.models import User, Todo, Label

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('todo.app'))
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user is not None and user.validate_password(password):
            login_user(user)
            return jsonify(message='Login success')
        return jsonify(message='Invalid username or password'), 400

    return render_template('_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message='Logout success.')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user_exited = User.query.filter_by(username=username).first()
    if user_exited is not None:
        return jsonify(message='Username already exists'), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    label1 = Label(name='work', author=user)
    label2 = Label(name='learn', author=user)
    db.session.add_all([label1, label2])
    db.session.commit()

    todo1 = Todo(body='Register JusTdo', author=user, done=True, label=label1)
    todo2 = Todo(body='Create a new Todo', author=user, label=label1)
    todo3 = Todo(body='Learn Python this week', author=user, label=label2)
    todo4 = Todo(body='Life is short, I need Python', author=user, label=label2)
    db.session.add_all([todo1, todo2, todo3, todo4])
    db.session.commit()
    return jsonify(message='Register success')
