import unittest
import json
from app import app  # Import the Flask app

class TestMoodApi(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        # Use the /quote endpoint as in the tests
        self.url = "/quote"
    
    def test_deep_sadness(self):
        response = self.client.post(self.url,
                                    data=json.dumps({"message": "I feel so lost and alone, nothing seems to matter anymore."}),
                                    content_type="application/json")
        data = json.loads(response.data)
        self.assertIn("quote", data)
        self.assertIn("Deep sadness", data["quote"])

    def test_frustration(self):
        response = self.client.post(self.url,
                                    data=json.dumps({"message": "I'm tired of trying and failing, nothing ever works out for me."}),
                                    content_type="application/json")
        data = json.loads(response.data)
        self.assertIn("quote", data)
        self.assertIn("Frustration", data["quote"])

    def test_invalid_message(self):
        response = self.client.post(self.url,
                                    data=json.dumps({"message": "Just another day."}),
                                    content_type="application/json")
        data = json.loads(response.data)
        self.assertIn("quote", data)
        self.assertIn("No sadness", data["quote"])

if __name__ == "__main__":
    unittest.main()