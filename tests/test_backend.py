import unittest
import json
from backend.app import app

class BackendTestCase(unittest.TestCase):
    """Test cases for the backend API."""

    def setUp(self):
        """Set up test client before each test."""
        self.client = app.test_client()
        self.client.testing = True

    def test_healthcheck(self):
        """Test the health check endpoint."""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "running"})

    def test_get_sessions(self):
        """Test retrieving active dataset sessions."""
        response = self.client.get("/api/get_sessions")
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessions", response.json)

    def test_latest_session(self):
        """Test retrieving the latest session ID."""
        response = self.client.get("/latest_session")
        self.assertIn(response.status_code, [200, 404])  # Handle empty sessions case
        if response.status_code == 200:
            self.assertIn("session_id", response.json)

if __name__ == "__main__":
    unittest.main()
