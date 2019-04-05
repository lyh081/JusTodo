import os
import click
from flask import Flask, render_template, request, jsonify
from flask_login import current_user
from JusTodo.extensions import db, login_manager, csrf
from JusTodo.models import User, Todo, Label
from JusTodo.setting import config
from JusTodo.blueprints.auth import auth_bp
from JusTodo.blueprints.home import home_bp
from JusTodo.blueprints.todo import todo_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('JusTodo')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprint(app)
    register_template_context(app)
    register_errors(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_blueprint(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(todo_bp)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            active_todos = Todo.query.with_parent(current_user).filter_by(done=False).count()
        else:
            active_todos = None
        return dict(active_todos=active_todos)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors.html', code=400, info='Bad Request'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors.html', code=403, info='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        if request.accept_mimetypes.accept_json and \
                not request.accept_mimetypes.accept_html \
                or request.path.startswith('/api'):
            response = jsonify(code=404, message='The requested URL was not found on the server.')
            response.status_code = 404
            return response
        return render_template('errors.html', code=404, info='Page Not Found'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        response = jsonify(code=405, message='The method is not allowed for the requested URL.')
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.accept_mimetypes.accept_json and \
                not request.accept_mimetypes.accept_html \
                or request.host.startswith('api'):
            response = jsonify(code=500, message='An internal server error occurred.')
            response.status_code = 500
            return response
        return render_template('errors.html', code=500, info='Server Error'), 500


def register_commands(app):
    @app.cli.command()
    def initdb():
        db.create_all()
        username = 'Test'
        password = '123'
        user = User(username = username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        label1 = Label(name='work', author=user)
        label2 = Label(name='learn', author=user)
        db.session.add_all([label1, label2])
        db.session.commit()

        todo1 = Todo(body='Witness something truly majestic', author=user, label=label1)
        todo2 = Todo(body='Help a complete stranger', author=user, label=label1)
        todo3 = Todo(body='Drive a motorcycle on the Great Wall of China', author=user, label=label2)
        todo4 = Todo(body='Sit on the Great Egyptian Pyramids', author=user, done=True, label=label2)
        db.session.add_all([todo1, todo2, todo3, todo4])
        db.session.commit()
        click.echo('Initialized database.')
