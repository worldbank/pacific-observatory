import sys
import unittest
from src.scraper.scrape import WebScraper


class TestWebScraper(unittest.TestCase):
    def setUp(self):
        # Initialize WebScraper for testing case
        self.web_scraper = WebScraper()

    def tearDown(self):
        pass

    def test_request_url(self):
        # Test the request_url method
        url = "https://example.com"
        content = self.web_scraper.request_url(url)
        self.assertIsNotNone(content)

    def test_extract_items(self):
        # Test the extract_items method
        content = b"<html><body><p>Item 1</p><p>Item 2</p></body></html>"
        parsed_content = self.web_scraper.parse_content(content)
        expression = "//p"
        items = self.web_scraper.extract_items(parsed_content, expression)
        self.assertEqual(len(items), 2)

    def test_scrape_url(self):
        # Test the scrape_url method
        url = "https://example.com"
        expression = "//p"
        items = self.web_scraper.scrape_url(url, expression)
        self.assertTrue(isinstance(items, list))


if __name__ == "__main__":
    unittest.main()
