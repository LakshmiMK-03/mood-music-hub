import unittest
import json
import os
import sys

# Add the project root to the python path so 'src' can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app
from src.services import supabase_service

class AuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the Flask test client and ensure the environment is ready."""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        
        cls.test_email = "lakshmi@gmail.com"
        cls.test_password = "test123"
        cls.test_name = "LakshmiTest"

    def test_1_registration(self):
        """Test user registration with a test case."""
        # Cleanup pre-existing user if present to ensure reliable test
        # Note: Depending on your database policies, this might require admin privileges.
        # supabase_service.delete_user(self.test_email) # Uncomment if you enable a robust delete method

        payload = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.client.post(
            '/api/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        # It should either succeed, or fail only because the email/username is already registered
        if response.status_code == 200:
            self.assertTrue(data.get('success'))
            self.assertEqual(data.get('message'), 'Registration successful!')
        else:
            self.assertEqual(response.status_code, 400)
            self.assertIn("already", data.get('error', '').lower())

    def test_2_login(self):
        """Test login for the test user."""
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.client.post(
            '/api/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('message'), 'Login successful!')
        self.assertIn('user', data)
        self.assertTrue(data['user']['name'].lower() in [self.test_name.lower(), 'lakshmi'] ) # Fallback for pre-existing records

if __name__ == '__main__':
    unittest.main()
