from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from JusTodo.extensions import db
from JusTodo.models import Todo, Label

todo_bp = Blueprint('todo', __name__)


@todo_bp.route('/app')
@login_required
def app():
    all_count = Todo.query.with_parent(current_user).count()
    active_count = Todo.query.with_parent(current_user).filter_by(done=False).count()
    completed_count = Todo.query.with_parent(current_user).filter_by(done=True).count()
    labels = Label.query.with_parent(current_user).all()
    todos = Todo.query.with_parent(current_user).all()
    return render_template('_app.html', todos=todos, all_count=all_count,
                           active_count=active_count, completed_count=completed_count,
                           labels=labels)


@todo_bp.route('/todo/new', methods=['POST'])
@login_required
def new_todo():
    data = request.get_json()
    if data is None or data['body'] == '':
        return jsonify(message='Invalid todo'), 400
    label = Label.query.with_parent(current_user).filter_by(name=data['label']).first()
    if label is None:
        label = Label(name=data['label'], author=current_user)
        db.session().add(label)
        db.session().commit()
    todo = Todo(body=data['body'], author=current_user, label=label)
    db.session.add(todo)
    db.session.commit()
    return jsonify(html=render_template('_todo.html', todo=todo), message='+1')


@todo_bp.route('/todo/<int:todo_id>/toggle', methods=['PATCH'])
@login_required
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if current_user != todo.author:
        return jsonify(message='Permission denied'), 403

    todo.done = not todo.done
    db.session.commit()
    return jsonify(message='Todo toggled.')


@todo_bp.route('/todo/<int:todo_id>/delete', methods=['DELETE'])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if current_user != todo.author:
        return jsonify(message='Permission denied.'), 403
    db.session.delete(todo)
    db.session.commit()
    return jsonify(message='Delete Success.')


@todo_bp.route('/todo/<string:label_name>/show', methods=['GET'])
@login_required
def show_todo(label_name):
    if label_name == 'all':
        todos = Todo.query.with_parent(current_user).all()
        return jsonify(html=render_template('_todos.html', todos=todos))
    label = Label.query.with_parent(current_user).filter_by(name=label_name).first()
    todos = Todo.query.with_parent(current_user).filter_by(label=label)
    return jsonify(html=render_template('_todos.html', todos=todos))


@todo_bp.route('/todo/refresh_nav', methods=['GET'])
@login_required
def refresh_nav():
    labels = Label.query.with_parent(current_user).all()
    all_count = Todo.query.with_parent(current_user).count()
    for label in labels:
        if Todo.query.with_parent(current_user).filter_by(label=label).count() == 0:
            db.session.delete(label)
            db.session.commit()
    labels = Label.query.with_parent(current_user).all()
    return jsonify(html=render_template('_sidenav.html', labels=labels, all_count=all_count))
