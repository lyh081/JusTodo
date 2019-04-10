from flask import url_for
from JusTodo.models import Todo


def todo_schema(todo):
    return {
        'id': todo.id,
        'self': url_for('.todo', todo_id=todo.id, _external=True),
        'kind': 'Todo',
        'body': todo.body,
        'done': todo.done,
        'author': {
            'id': todo.author.id,
            'username': todo.author.username,
            'url': url_for('.user', _external=True),
            'kind': 'User',
        },
    }


def user_schema(user):
    return {
        'id': user.id,
        'self': url_for('.user', _external=True),
        'username': user.username,
        'kind': 'User',
        'all_todo_count': len(user.todo),
        'all_todo_url': url_for('.todos', _external=True),
        'active_todo_count': Todo.query.with_parent(user).filter_by(done=False).count(),
        'completed_item_count': Todo.query.with_parent(user).filter_by(done=True).count(),
    }


def todos_schema(todos):
    return {
        'kind': 'TodoCollection',
        'self': url_for('.user', _external=True),
        'todos': [todo_schema(todo) for todo in todos],
        'count': len(todos),
    }