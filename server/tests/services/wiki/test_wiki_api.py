from unittest.mock import patch

from flask import url_for

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.wiki.mediawiki_service import MediaWikiServiceError


class TestWikiDocumentApi(BaseTestCase):
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
        expected = {"detail": self.fail_post_message}
        self.assertEqual(expected, response.json)

    @patch("server.services.wiki.pages.utils.generate_document_data_from_wiki_pages")
    def test_wiki_document_patch_fails_with_invalid_project(
        self, mocked_generate_document_data
    ):
        with patch("server.services.wiki.pages.utils.OverviewPageService"), patch(
            "server.services.wiki.pages.utils.OrganisationPageService"
        ) as mocked_organisation_page, patch(
            "server.services.wiki.pages.utils.ProjectPageService"
        ) as mocked_project_page:
            organisation_page_data = {
                "project": [{"name": "Organisation project example"}],
                "organisation": {"name": "Organisation name"},
                "platform": {"name": "Platform name"},
            }
            mocked_organisation_page.return_value.parse_page_to_serializer.return_value = (
                organisation_page_data
            )

            project_page_data = {"project": {"name": "Project example"}}
            mocked_project_page.return_value.parse_page_to_serializer.return_value = (
                project_page_data
            )

            error_message = (
                f"Error editing project '{project_page_data['project']['name']}'. "
                "Project does not belong to the organisation "
                f"'{organisation_page_data['organisation']['name']}'."
            )
            mocked_generate_document_data.side_effect = MediaWikiServiceError("Error")

            response = self.client.patch(
                url_for(
                    "update_wiki_document",
                    organisation_name=self.document_data["organisation"]["name"],
                    project_name=self.document_data["project"]["name"],
                ),
                json=self.document_data,
            )
            expected = {"detail": error_message}
            self.assertEqual(expected, response.json)

    @patch("server.api.wiki.resources.generate_document_data_from_wiki_pages")
    def test_wiki_document_patch_fails(self, mocked_generate_document_data):
        with patch(
            "server.api.wiki.resources.OverviewPageService.edit_page"
        ) as mocked_overview_page, patch(
            "server.api.wiki.resources.OrganisationPageService.edit_page"
        ) as mocked_organisation_page, patch(
            "server.api.wiki.resources.ProjectPageService.edit_page"
        ) as mocked_project_page:
            updated_document = {"project": {"name": "updated project name"}}
            current_document = {"project": {"name": "project name"}}
            mocked_generate_document_data.return_value = (
                {"project": {"name": "updated project name"}},
                {"project": {"name": "project name"}},
            )
            self.client.patch(
                url_for(
                    "update_wiki_document",
                    organisation_name=self.document_data["organisation"]["name"],
                    project_name=self.document_data["project"]["name"],
                ),
                json=self.document_data,
            )
            mocked_overview_page.assert_called_with(
                updated_document, self.document_data, current_document
            )
            mocked_organisation_page.assert_called_with(
                updated_document, self.document_data, current_document
            )
            mocked_project_page.assert_called_with(
                updated_document, self.document_data, current_document
            )

    @patch("server.services.wiki.pages.overview_service.MediaWikiService")
    @patch("server.api.wiki.resources.generate_document_data_from_wiki_pages")
    def test_wiki_document_patch_fails_with_invalid_mediawiki_token(
        self, mocked_generate_document_data, mocked_mediawiki
    ):
        mocked_generate_document_data.return_value = (
            {"project": {"name": "updated project name"}},
            {"project": {"name": "project name"}},
        )
        mocked_mediawiki.return_value.get_token.side_effect = MediaWikiServiceError(
            "Invalid token"
        )
        response = self.client.patch(
            url_for(
                "update_wiki_document",
                organisation_name=self.document_data["organisation"]["name"],
                project_name=self.document_data["project"]["name"],
            ),
            json=self.document_data,
        )
        expected_response = {"detail": "Invalid token"}
        self.assertEqual(expected_response, response.json)
