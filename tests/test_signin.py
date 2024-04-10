import unittest
from app import app, db
from app.model import User, Post
from werkzeug.security import generate_password_hash
from app.blogApp import generate_token

class SigninTest(unittest.TestCase):

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
        hashed_password = generate_password_hash('test_password')
        test_user = User(username='test_user', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    

    # Test signin with correct credentials
    def test_signin_correct_credentials(self):
        signup_data = {'username': 'test_user', 'password': 'test_password'}
        self.app.post('/signup', json=signup_data)
        signin_data = {'username': 'test_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)


    # Test signin with incorrect password
    def test_signin_incorrect_password(self):
        signin_data = {'username': 'test_user', 'password': 'wrong_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid username or password!', response.data)


    # Test signin with non-existing username
    def test_signin_non_existing_username(self):
        signin_data = {'username': 'non_existing_user', 'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid username or password!', response.data)


    # Test signin with missing username
    def test_signin_missing_username(self):
        signin_data = {'password': 'test_password'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username and password are required!', response.data)


    # Test signin with missing password
    def test_signin_missing_password(self):
        signin_data = {'username': 'test_user'}
        response = self.app.post('/signin', json=signin_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username and password are required!', response.data)