from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.services.wiki.mediawiki_service import (
    MediaWikiService,
    MediaWikiServiceError,
)


@patch("server.services.wiki.mediawiki_service.requests.Session")
class TestMediaWikiService(BaseTestCase):
    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_get_page_text(self, mocked_session):
        mediawiki = MediaWikiService()
        page_title = "example page"
        get_page_params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }
        mocked_session.return_value.get.return_value.json.return_value = {
            "parse": {"wikitext": {"*": "page text"}}
        }
        mediawiki.get_page_text(page_title)
        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_page_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_get_page_text_fails_without_existing_page(self, mocked_session):
        mediawiki = MediaWikiService()
        page_title = "non existing page"
        mocked_session.return_value.get.return_value.json.return_value = {
            "error": {"code": "missingtitle"}
        }
        with self.assertRaises(MediaWikiServiceError):
            mediawiki.get_page_text(page_title)

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_existing_page(self, mocked_session):
        mediawiki = MediaWikiService()
        page_title = "existing page"
        get_page_params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }

        mocked_session.return_value.get.return_value.json.return_value = {
            "parse": {"wikitext": {"*": "page text"}}
        }
        existing_page = mediawiki.is_existing_page(page_title)
        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_page_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()
        self.assertTrue(existing_page)

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_non_existing_page(self, mocked_session):
        mediawiki = MediaWikiService()
        page_title = "existing page"
        get_page_params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }

        mocked_session.return_value.get.return_value.json.return_value = {
            "error": {"code": "missingtitle"}
        }
        existing_page = mediawiki.is_existing_page(page_title)
        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_page_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()
        self.assertFalse(existing_page)

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_create_page(self, mocked_session):
        mocked_session.return_value.post.return_value.json.return_value = {
            "edit": {"result": "Success"}
        }

        page_title = "page title example"
        post_page_params = {
            "action": "edit",
            "title": page_title,
            "createonly": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json",
        }

        token = "token example"
        page_text = "page text example"
        post_json_data = {"token": token, "text": page_text}

        mediawiki = MediaWikiService()
        mediawiki.create_page(token, page_title, page_text)
        mocked_session.return_value.post.assert_called_with(
            url="https://your-wiki.org/api.php",
            params=post_page_params,
            data=post_json_data,
        )
        mocked_session.return_value.post.return_value.json.assert_called_with()

    def test_create_page_fails_with_existing_page(self, mocked_session):
        mediawiki = MediaWikiService()
        mocked_session.return_value.post.return_value.json.return_value = {
            "error": {"code": "articleexists"}
        }
        with self.assertRaises(MediaWikiServiceError):
            token = "token example"
            page_title = "page title example"
            page_text = "page text example"
            mediawiki.create_page(token, page_title, page_text)

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_edit_page(self, mocked_session):
        mocked_session.return_value.post.return_value.json.return_value = {
            "edit": {"result": "Success"}
        }

        page_title = "page title example"
        post_page_params = {
            "action": "edit",
            "title": page_title,
            "nocreate": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json",
        }

        token = "token example"
        page_text = "page text example"
        post_json_data = {"token": token, "text": page_text}

        mediawiki = MediaWikiService()
        mediawiki.edit_page(token, page_title, page_text)
        mocked_session.return_value.post.assert_called_with(
            url="https://your-wiki.org/api.php",
            params=post_page_params,
            data=post_json_data,
        )
        mocked_session.return_value.post.return_value.json.assert_called_with()

    def test_edit_page_fails_with_non_existing_page(self, mocked_session):
        mediawiki = MediaWikiService()
        mocked_session.return_value.post.return_value.json.return_value = {
            "error": {"code": "missingtitle"}
        }
        with self.assertRaises(MediaWikiServiceError):
            token = "token example"
            page_title = "page title example"
            page_text = "page text example"
            mediawiki.edit_page(token, page_title, page_text)

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_is_valid_token(self, mocked_session):
        mediawiki = MediaWikiService()
        mocked_session.return_value.post.return_value.json.return_value = {
            "checktoken": {"result": "valid"}
        }

        token = "token example"
        post_json_data = {"token": token}

        post_page_params = {"action": "checktoken", "type": "csrf", "format": "json"}

        is_valid_token = mediawiki.is_valid_token(token)
        mocked_session.return_value.post.assert_called_with(
            url="https://your-wiki.org/api.php",
            params=post_page_params,
            data=post_json_data,
        )
        mocked_session.return_value.post.return_value.json.assert_called_with()
        self.assertTrue(is_valid_token)

    def test_is_valid_token_fails_with_invalid_token(self, mocked_session):
        mediawiki = MediaWikiService()
        mocked_session.return_value.post.return_value.json.return_value = {
            "checktoken": {"result": "invalid"}
        }
        token = "invalid token example"
        is_valid_token = mediawiki.is_valid_token(token)
        self.assertFalse(is_valid_token)

    @patch(
        "server.services.wiki.mediawiki_service.MediaWikiService.is_valid_token",
        return_value=True,
    )
    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_get_token(self, mocked_valid_token, mocked_session):
        mediawiki = MediaWikiService()
        get_page_params = {"action": "query", "meta": "tokens", "format": "json"}

        expected_token = "supersecrettoken"
        mocked_session.return_value.get.return_value.json.return_value = {
            "query": {"tokens": {"csrftoken": expected_token}}
        }
        token = mediawiki.get_token()
        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_page_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()
        self.assertEqual(expected_token, token)

    @patch(
        "server.services.wiki.mediawiki_service.MediaWikiService.is_valid_token",
        return_value=False,
    )
    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_get_token_fails_with_invalid_token(
        self, mocked_valid_token, mocked_session
    ):
        mediawiki = MediaWikiService()
        get_page_params = {"action": "query", "meta": "tokens", "format": "json"}

        with self.assertRaises(MediaWikiServiceError):
            mocked_session.return_value.get.return_value.json.return_value = {
                "query": {"tokens": {"csrftoken": "invalid token"}}
            }
            mediawiki.get_token()

        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_page_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()

    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_generate_login_token(self, mocked_session):
        mediawiki = MediaWikiService()
        get_params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "login",
        }
        mediawiki.generate_login_token()

        mocked_session.return_value.get.assert_called_with(
            url="https://your-wiki.org/api.php", params=get_params
        )
        mocked_session.return_value.get.return_value.json.assert_called_with()

    @patch(
        "server.services.wiki.mediawiki_service.MediaWikiService.generate_login_token",
        return_value="login token",
    )
    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {"WIKI_API_ENDPOINT": "https://your-wiki.org/api.php"},
    )
    def test_login_fails_with_invalid_credentials(
        self, mocked_login_token, mocked_session
    ):
        mediawiki = MediaWikiService()
        mocked_session.return_value.post.return_value.json.return_value = {
            "login": {"result": "Failed"}
        }
        with self.assertRaises(MediaWikiServiceError):
            mocked_session.return_value.get.return_value.json.return_value = {
                "query": {"tokens": {"csrftoken": "invalid token"}}
            }
            mediawiki.login()

    @patch(
        "server.services.wiki.mediawiki_service.MediaWikiService.generate_login_token",
        return_value="login token",
    )
    @patch.dict(
        "server.services.wiki.mediawiki_service.current_app.config",
        {
            "WIKI_API_ENDPOINT": "https://your-wiki.org/api.php",
            "MEDIAWIKI_BOT_NAME": "bot name",
            "MEDIAWIKI_BOT_PASSWORD": "bot password",
        },
    )
    def test_login(self, mocked_login_token, mocked_session):
        mediawiki = MediaWikiService()
        post_page_params = {"action": "login", "lgname": "bot name", "format": "json"}
        post_json_data = {"lgpassword": "bot password", "lgtoken": "login token"}
        mediawiki.login()

        mocked_session.return_value.post.assert_called_with(
            url="https://your-wiki.org/api.php",
            params=post_page_params,
            data=post_json_data,
        )
        mocked_session.return_value.post.return_value.json.assert_called_with()
