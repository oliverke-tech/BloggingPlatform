import unittest
from app import app

class TestApp(unittest.TestCase):

    def test_signup(self):
        tester = app.test_client(self)
        response = tester.post('/signup', json={'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User created successfully!', response.data)

if __name__ == '__main__':
    unittest.main()