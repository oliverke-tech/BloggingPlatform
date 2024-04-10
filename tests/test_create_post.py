import unittest
from app import app, db
from app.model import User, Post
from werkzeug.security import generate_password_hash
from app.blogApp import generate_token

class CreatePostTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
        app.config['SECRET_KEY'] = 'my_secret_key'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        # Create a test user
        test_user = User(username='test_user', password='test_password')
        db.session.add(test_user)
        db.session.commit()

        # Generate token for authentication
        self.token = generate_token('test_user')


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    

    # Test creating a new post with correct data
    def test_create_post(self):
        post_data = {'title': 'Test Post', 'content': 'This is a test post content'}
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)


    # Test creating a new post with missing title
    def test_create_post_missing_title(self):
        post_data = {'content': 'This is a test post content'}
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title and content are required!', response.data)


    # Test creating a new post with missing content
    def test_create_post_missing_content(self):
        post_data = {'title': 'Test Post'}
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.post('/posts', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title and content are required!', response.data)