import unittest
import json
from app import app, db
from app.model import User, Post
from werkzeug.security import generate_password_hash
from app.blogApp import generate_token

class GetPostTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
        app.config['SECRET_KEY'] = 'my_secret_key'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test posts
        test_user = User(username='test_user', password='test_password')
        db.session.add(test_user)
        db.session.commit()

        test_post_1 = Post(title='Test Post 1', content='This is test post 1', author='test_user')
        test_post_2 = Post(title='Test Post 2', content='This is test post 2', author='test_user')
        db.session.add(test_post_1)
        db.session.add(test_post_2)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    

    # Test retrieving all posts
    def test_get_all_posts(self):
        response = self.app.get('/posts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)  # Assuming there are 2 test posts
        self.assertEqual(data[0]['title'], 'Test Post 1')
        self.assertEqual(data[1]['title'], 'Test Post 2')

    # Test retrieving a specific post by ID
    def test_get_specific_post(self):
        # Assuming post_id 1 exists
        response = self.app.get('/posts/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Test Post 1')

    # Test retrieving a non-existing post by ID
    def test_get_non_existing_post(self):
        # Assuming post_id 999 does not exist
        response = self.app.get('/posts/999')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Post not found!')