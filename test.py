import unittest
from app import app, db
from app.model import User, Post
import json
from app.blogApp import generate_token

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
        app.config['SECRET_KEY'] = 'your_secret_key'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def test_signup(self):
        response = self.app.post('/signup', json={'username': 'test_user', 'password': 'test_password'})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User created successfully!')
        self.assertEqual(data['username'], 'test_user')

    def test_signin(self):
        # First, signup a user
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        self.app.post('/signup', json=signup_data)

        # Now try to sign in
        signin_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)

    def test_create_post(self):
        # First, signup a user
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        self.app.post('/signup', json=signup_data)

        # Sign in to get the token
        signin_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        token = json.loads(response.data)['token']

        # Now create a post
        post_data = {'title': 'Test Post', 'content': 'This is a test post'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)

    def test_update_post(self):
        # First, signup a user
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        self.app.post('/signup', json=signup_data)

        # Sign in to get the token
        signin_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        token = json.loads(response.data)['token']

        # First, create a post
        post_data = {'title': 'Test Post', 'content': 'This is a test post'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)

        # Retrieve the post ID
        response = self.app.get('/posts')
        post_id = json.loads(response.data)[0]['id']

        # Update the post
        updated_post_data = {'title': 'Updated Test Post', 'content': 'This is an updated test post'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.app.put(f'/posts/{post_id}', json=updated_post_data, headers=headers)

        # Check if the post was updated successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post updated successfully!', response.data)

    def test_delete_post(self):
        # First, signup a user
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        self.app.post('/signup', json=signup_data)

        # Sign in to get the token
        signin_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 200)
        token = response.json['token']

        # Create a post
        post_data = {'title': 'Test Post', 'content': 'This is a test post'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)

        # Retrieve the post ID
        response = self.app.get('/posts')
        post_id = response.json[0]['id']

        # Delete the post
        response = self.app.delete(f'/posts/{post_id}', headers=headers)

        # Check if the post was deleted successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post deleted successfully!', response.data)


if __name__ == '__main__':
    unittest.main()