import re

from flask import current_app

import requests


class MediaWikiServiceError(Exception):
    """
    Custom Exception to notify callers an error occurred when handling wiki
    """

    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class MediaWikiService:
    def __init__(self):
        self.endpoint = current_app.config["WIKI_API_ENDPOINT"]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": f"{current_app.config['OEG_REPORTER_BOT_NAME']}/"
                f"{current_app.config['OEG_REPORTER_VERSION']}"
                f" ({current_app.config['OEG_REPORTER_CONTACT_INFORMATION']})"
            }
        )
        self.login()

    def get_page_text(self, page_title: str) -> str:
        """
        Get the page content of a page parsed as Wikitext

        Keyword arguments:
        page_title -- The title of the page

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki

        Returns:
        text -- The text of the page
        """
        params = {
            "action": "parse",
            "maxlag": "5",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }
        r = self.session.get(url=self.endpoint, params=params)
        data = r.json()
        if "error" in list(data.keys()) and data["error"]["code"] == "missingtitle":
            raise MediaWikiServiceError(
                f"Error getting text from the page '{page_title}'."
                " Page does not exist."
            )
        else:
            text = data["parse"]["wikitext"]["*"]
            return text

    def is_existing_page(self, page_title: str) -> str:
        """
        Get the page content of a page parsed as Wikitext

        Keyword arguments:
        page_title -- The title of the page

        Returns:
        text -- The text of the page
        """
        params = {
            "action": "parse",
            "maxlag": "5",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
        }
        r = self.session.get(url=self.endpoint, params=params)
        data = r.json()
        if "error" in list(data.keys()) and data["error"]["code"] == "missingtitle":
            return False
        else:
            return True

    def create_page(self, token: str, page_title: str, page_text: str) -> dict:
        """
        Create a new wiki page

        Keyword arguments:
        token -- The MediaWiki API token
        page_title -- The title of the page being created
        page_text -- The text of the page being created

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for creating
                the page
        """
        params = {
            "action": "edit",
            "maxlag": "5",
            "title": page_title,
            "createonly": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json",
        }
        r = self.session.post(
            url=self.endpoint,
            params=params,
            data={"token": token, "text": str(page_text)},
        )
        data = r.json()
        if "error" in list(data.keys()) and data["error"]["code"] == "articleexists":
            raise MediaWikiServiceError(
                f"Error creating the page '{page_title}'." " Page already exists"
            )
        else:
            return data

    def edit_page(self, token: str, page_title: str, page_text: str) -> dict:
        """
        Edit a existing wiki page

        Keyword arguments:
        token -- The MediaWiki API token
        page_title -- The title of the page being created
        page_text -- The text of the page being created

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for creating
                the page
        """
        params = {
            "action": "edit",
            "maxlag": "5",
            "title": page_title,
            "nocreate": "true",
            "contentmodel": "wikitext",
            "bot": "true",
            "format": "json",
        }
        r = self.session.post(
            url=self.endpoint,
            params=params,
            data={"token": token, "text": str(page_text)},
        )
        data = r.json()
        if "error" in list(data.keys()) and data["error"]["code"] == "missingtitle":
            raise MediaWikiServiceError(
                f"Error editing the page '{page_title}'. Page does not exist"
            )
        else:
            return data

    def move_page(self, token: str, old_page: str, new_page: str):
        """
        Edit a existing wiki page

        Keyword arguments:
        token -- The MediaWiki API token
        page_title -- The title of the page being created
        page_text -- The text of the page being created

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki

        Returns:
        data -- Dictionary with result of post request for creating
                the page
        """
        params = {
            "action": "move",
            "maxlag": "5",
            "from": old_page,
            "to": new_page,
            "movetalk": "true",
            "format": "json",
        }
        r = self.session.post(url=self.endpoint, params=params, data={"token": token})
        data = r.json()
        if "error" in list(data.keys()) and data["error"]["code"] == "selfmove":
            raise MediaWikiServiceError(
                f"Error moving page from '{old_page}' to '{new_page}'."
                " Both pages have the same title."
            )
        else:
            return data

    def is_redirect_page(self, page_text: str):
        redirect_page = re.search(r"#REDIRECT\s\[\[(.*?)\]\]", page_text)
        if redirect_page:
            return redirect_page.groups()[0]
        else:
            return False

    def is_valid_token(self, token: str) -> dict:
        """
        Check if MediaWiki API Token is valid

        Keyword arguments:
        token -- The MediaWiki API token

        Returns:
        data -- Dictionary with result of post request for checking
                the MediaWiki API Token
        """
        params = {
            "action": "checktoken",
            "maxlag": "5",
            "type": "csrf",
            "format": "json",
        }
        r = self.session.post(url=self.endpoint, params=params, data={"token": token})
        data = r.json()
        if data["checktoken"]["result"] == "invalid":
            return False
        else:
            return True

    def get_token(self) -> str:
        """
        Get MediaWiki API Token for an active Session

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki

        Returns:
        token -- MediaWiki API Token for an active Session
        """
        params = {"action": "query", "maxlag": "5", "meta": "tokens", "format": "json"}
        r = self.session.get(url=self.endpoint, params=params)
        data = r.json()
        token = data["query"]["tokens"]["csrftoken"]
        if self.is_valid_token(token):
            return token
        else:
            raise MediaWikiServiceError("Invalid MediaWiki API Token")

    def generate_login_token(self) -> str:
        """
        Generate Login Token for MediaWiki API

        Returns:
        token -- Login Token for MediaWiki API
        """
        params_token = {
            "action": "query",
            "maxlag": "5",
            "format": "json",
            "meta": "tokens",
            "type": "login",
        }
        r = self.session.get(url=self.endpoint, params=params_token)
        data = r.json()
        login_token = data["query"]["tokens"]["logintoken"]
        return login_token

    def login(self) -> None:
        """
        Login into MediaWiki API

        Raises:
        MediaWikiServiceError -- Exception raised when handling wiki
        """
        login_token = self.generate_login_token()
        params_login = {
            "action": "login",
            "maxlag": "5",
            "lgname": current_app.config["MEDIAWIKI_BOT_NAME"],
            "format": "json",
        }
        r = self.session.post(
            url=self.endpoint,
            params=params_login,
            data={
                "lgpassword": current_app.config["MEDIAWIKI_BOT_PASSWORD"],
                "lgtoken": login_token,
            },
        )
        data = r.json()
        if "login" in data.keys() and data["login"]["result"] == "Failed":
            raise MediaWikiServiceError("Invalid MediaWiki bot credentials")
