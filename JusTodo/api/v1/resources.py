from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView
from JusTodo.api.v1 import api_v1
from JusTodo.api.v1.errors import api_abort, ValidationError
from JusTodo.api.v1.auth import generate_token, auth_required
from JusTodo.models import User, Todo, Label
from JusTodo.extensions import db
from JusTodo.api.v1.schemas import todo_schema, user_schema, todos_schema

def get_body_label():
    data = request.get_json()
    body = data.get('body')
    label_name = data.get('label_name')
    if body is None or str(body).strip() == '':
        raise ValidationError('body or label was empty or invalid.')
    if label_name is None or str(label_name).strip() == '':
        raise ValidationError('body or label was empty or invalid.')
    return body, label_name

class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": url_for('.index', _external=True),
            "current_user_url": url_for('.user',_external=True),
            "authentication_url": url_for('.token', _external=True),
            "todo_url": url_for('.todo', todo_id=1, _external=True),
            "current_user_todos_url": url_for('.todos', _external=True)

        })


api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])


class AuthTokenAPI(MethodView):

    def post(self):
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')

        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            return api_abort(code=400, message='Invalid username or passsword')

        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })

        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'

        return response


api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])


class TodoAPI(MethodView):
    decorators = [auth_required]

    def get(self, todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if g.current_user != todo.author:
            return api_abort(403)
        return jsonify(todo_schema(todo))

    def put(self, todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if g.current_user != todo.author:
            return api_abort(403)
        todo.body = get_body()
        db.session.commit()
        return jsonify(todo_schema(todo))

    def patch(self, todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if g.current_user != todo.author:
            return api_abort(403)
        todo.done = not todo.done
        db.session.commit()
        return '', 204

    def delete(self, todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if g.current_user != todo.author:
            return api_abort(403)
        db.session.delete(todo)
        db.session.commit()
        return '', 204


api_v1.add_url_rule('/user/todo/<int:todo_id>', view_func=TodoAPI.as_view('todo'),
                    methods=['GET', 'PUT', 'PATCH', 'DELETE'])


class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify(user_schema(g.current_user))


api_v1.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])


class TodosAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        todos = Todo.query.with_parent(g.current_user).all()
        return jsonify(todos_schema(todos))

    def post(self):
        body, label_name = get_body_label()
        label = Label.query.with_parent(g.current_user).filter_by(name=label_name).first()
        if label is None:
            label = Label(name=label, author=g.current_user)
            db.session().add(label)
            db.session().commit()
        todo = Todo(body=body, author=g.current_user, label=label)
        db.session.add(todo)
        db.session.commit()

        response = jsonify(todo_schema(todo))
        response.status_code = 201
        response.headers['Location'] = url_for('.todo', todo_id=todo.id, _external=True)
        return response


api_v1.add_url_rule('/user/todos', view_func=TodosAPI.as_view('todos'), methods=['GET', 'POST'])
