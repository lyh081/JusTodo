import unittest
from flask import url_for

from JusTodo import create_app, db
from JusTodo.models import User, Todo, Label


class APITestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

        user1 = User(username='Admin')
        user1.set_password('000')
        label = Label(name='test label',author=user1)
        todo1 = Todo(body='Test Todo', author=user1, label=label)

        user2 = User(username='Test')
        user2.set_password('123')
        todo2 = Todo(body='Test todo 2', author=user2, label=label)

        db.session.add_all([todo1, todo2])
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def get_oauth_token(self):
        response = self.client.post(url_for('api_v1.token'), data=dict(
            grant_type='password',
            username='Admin',
            password='000'
        ))
        data = response.get_json()
        return data['access_token']

    def set_auth_headers(self, token):
        return {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_api_index(self):
        response = self.client.get(url_for('api_v1.index'))
        data = response.get_json()
        self.assertEqual(data.get('api_version'),'1.0')

    def test_get_token(self):
        response = self.client.post(url_for('api_v1.token'), data=dict(
            grant_type='password',
            username='Admin',
            password='000'
        ))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', data)

    def test_get_user(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.user'), headers=self.set_auth_headers(token))

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'Admin')

    def test_get_todo(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.todo', todo_id=1), headers=self.set_auth_headers(token))

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], 1)
        self.assertIn('id', data)
        self.assertIn('self', data)
        self.assertIn('body', data)
        self.assertIn('author', data)

    def test_toggle_todo(self):
        token = self.get_oauth_token()
        done = not Todo.query.get(1).done
        response = self.client.patch(url_for('api_v1.todo', todo_id=1), headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Todo.query.get(1).done, done)

    def test_delete_todo(self):
        token = self.get_oauth_token()
        response = self.client.delete(url_for('api_v1.todo', todo_id=1), headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Todo.query.get(1), None)

    def test_new_todo(self):
        token = self.get_oauth_token()
        response = self.client.post(url_for('api_v1.todos'),
                                    json=dict(body='New a Todo', label_name='Test'),
                                    headers=self.set_auth_headers(token))
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['body'], 'New a Todo')

        response = self.client.post(url_for('api_v1.todos'),
                                   json=dict(body='',label_name=''),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'body or label was empty or invalid.')

    def test_get_todos(self):
        user = User.query.get(1)
        todo2 = Todo(body='Test todo 2', author=user)
        todo3 = Todo(body='Test todo 3', author=user)
        todo4 = Todo(body='Test todo 4', author=user, done=True)
        db.session.commit()

        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.todos'),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('self', data)
        self.assertIn('todos', data)
        self.assertEqual(data['count'], 4)



