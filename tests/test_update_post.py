import unittest
from app import app, db
from app.model import User, Post
from werkzeug.security import generate_password_hash
from app.blogApp import generate_token

class UpdatePostTest(unittest.TestCase):

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

        # Create a test post by the test user
        test_post = Post(title='Test Post', content='This is a test post content', author='test_user')
        db.session.add(test_post)
        db.session.commit()

        # Generate token for authentication
        self.token = generate_token('test_user')


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    

    # Test updating a post with correct data
    def test_update_post(self):
        post_data = {'title': 'Updated Post Title', 'content': 'Updated post content'}
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.put('/posts/1', json=post_data, headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post updated successfully!', response.data)


    # Test updating a non-existing post
    def test_update_non_existing_post(self):
        post_data = {'title': 'Updated Post Title', 'content': 'Updated post content'}
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.put('/posts/999', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Post not found!', response.data)


    # Test updating a post by unauthorized user
    def test_update_post_unauthorized_user(self):
        # Create another test user
        unauthorized_user = User(username='unauthorized_user', password='unauthorized_password')
        db.session.add(unauthorized_user)
        db.session.commit()

        # Generate token for unauthorized user
        unauthorized_token = generate_token('unauthorized_user')

        post_data = {'title': 'Updated Post Title', 'content': 'Updated post content'}
        headers = {'Authorization': f'Bearer {unauthorized_token}'}
        response = self.app.put('/posts/1', json=post_data, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'You are not authorized to update this post!', response.data)
        