from unittest.mock import patch

from flask import url_for

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.wiki.mediawiki_service import MediaWikiServiceError


class TestGitDocumentApi(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.document_data = utils.document_data
        self.success_post_message = (
            f"Document for project {self.document_data['project']['projectId']} created"
        )
        self.fail_post_message = "The page you specified already exist"

    @patch("server.services.wiki.pages.project_service.ProjectPageService.create_page")
    @patch(
        "server.services.wiki.pages.organisation_service.OrganisationPageService.create_page"
    )
    @patch(
        "server.services.wiki.pages.overview_service.OverviewPageService.create_page"
    )
    def test_wiki_document_post(
        self, mocked_overview_page, mocked_organisation_page, mocked_project_page
    ):
        response = self.client.post(
            url_for("create_wiki_document"), json=self.document_data
        )
        expected = {"detail": self.success_post_message}
        self.assertEqual(expected, response.json)

        mocked_overview_page.assert_called_with(self.document_data)
        mocked_organisation_page.assert_called_with(self.document_data)
        mocked_project_page.assert_called_with(self.document_data)

    @patch(
        "server.services.wiki.pages.overview_service.OverviewPageService.create_page"
    )
    def test_wiki_document_post_fail_with_existing_page(self, mocked_overview_page):
        mocked_overview_page.side_effect = MediaWikiServiceError(self.fail_post_message)
        response = self.client.post(
            url_for("create_wiki_document"), json=self.document_data
        )
        expected = {"Error": self.fail_post_message}
        self.assertEqual(expected, response.json)
