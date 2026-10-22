
import unittest
from app import search_knowledge_base


class CloudPilotTests(unittest.TestCase):

    def test_http_503_search(self):
        results = search_knowledge_base(
            "Why is my application returning HTTP 503?"
        )
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0][1]["service"], "HTTP")

    def test_s3_access_denied_search(self):
        results = search_knowledge_base(
            "Why am I getting Access Denied in S3?"
        )
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0][1]["service"], "S3")


if __name__ == "__main__":
    unittest.main()
