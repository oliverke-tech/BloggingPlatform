import unittest
from app import app, db
from app.model import User, Post
from app.blogApp import generate_token

class SignupTest(unittest.TestCase):

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
    

    # Test successful signup
    def test_signup_valid_data(self):
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signup', json=signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User created successfully!', response.data)


    # Test signup with existing username
    def test_signup_existing_username(self):
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        
        # First signup attempt
        response = self.app.post('/signup', json=signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User created successfully!', response.data)
        
        # Second signup attempt with the same username
        response = self.app.post('/signup', json=signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username already exists!', response.data)


    # Test signup with missing username
    def test_signup_missing_username(self):
        signup_data = {'password': 'test_password'}
        response = self.app.post('/signup', json=signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username and password are required!', response.data)


    # Test signup with missing password
    def test_signup_missing_password(self):
        signup_data = {'username': 'test_user'}
        response = self.app.post('/signup', json=signup_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username and password are required!', response.data)