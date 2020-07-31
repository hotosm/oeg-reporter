from datetime import datetime

from server.tests.base_test_config import BaseTestCase
from server.services.wiki.wiki_text_service import WikiTextService


class TestWikiTextService(BaseTestCase):
    def test_hyperlink_external_link(self):
        hyperlynk_text = "text example"
        link = "http://example.com"
        expected_hyperlink = f"[{link} {hyperlynk_text}]"
        hyperlink = WikiTextService().hyperlink_external_link(hyperlynk_text, link)
        self.assertEqual(hyperlink, expected_hyperlink)

    def test_hyperlink_wiki_page(self):
        wiki_page = "Wikipage"
        text = "wiki page text"
        expected_hyperlink = f"[[{wiki_page} | {text}]]"
        hyperlink = WikiTextService().hyperlink_wiki_page(wiki_page, text)
        self.assertEqual(hyperlink, expected_hyperlink)

    def test_format_date_text(self):
        date = "2019-04-08T10:54:25.449637Z"
        parsed_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        expected_formatted_date = "08 April 2019"
        formatted_date = WikiTextService().format_date_text(parsed_date)
        self.assertEqual(expected_formatted_date, formatted_date)

    def test_format_date_text_fails_with_wrong_date(self):
        wrong_date = "2019-04-08T10:54:25.449637"

        with self.assertRaises(ValueError):
            WikiTextService().format_date_text(wrong_date)
