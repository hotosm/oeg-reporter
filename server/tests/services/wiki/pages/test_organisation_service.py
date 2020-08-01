from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.wiki.pages.organisation_service import OrganisationPageService


class TestOrganisationService(BaseTestCase):
    def setUp(self):
        self.document_data = utils.document_data
        self.organisation_data = {
            "organisation": {
                "name": self.document_data["organisation"]["name"],
                "description": self.document_data["organisation"]["description"],
                "url": self.document_data["organisation"]["url"],
            },
            "project": {
                "name": self.document_data["project"]["name"],
                "author": self.document_data["project"]["author"],
                "status": self.document_data["project"]["status"],
            },
            "platform": {
                "name": self.document_data["platform"]["name"],
                "url": self.document_data["platform"]["url"],
            },
        }
        self.templates = utils.OrganisationPageTemplates()

    def test_filter_page_data(self):
        organisation_page_data = OrganisationPageService().filter_page_data(
            self.document_data
        )
        organisation_is_subset = set(organisation_page_data.keys()).issubset(
            self.document_data.keys()
        )
        self.assertTrue(organisation_is_subset)

    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.hyperlink_external_link"
    )
    def test_generate_page_sections_dict(self, mocked_hyperlink):
        organisation_url = "[http://www.organisation.com Organisation name]"

        platform_url = "[http://www.platform.com Platform name]"
        mocked_hyperlink.side_effect = [organisation_url, platform_url]

        expected_sections = {
            self.templates.organisation_section: {
                self.templates.organisation_link_section: f"\n{organisation_url}\n",
                self.templates.organisation_description_section: (
                    f"\n{self.organisation_data['organisation']['description']}\n"
                ),
            },
            self.templates.platform_section: {
                self.templates.platform_link_section: f"\n{platform_url}\n",
            },
        }

        organisation_page_sections = OrganisationPageService().generate_page_sections_dict(
            self.organisation_data
        )
        self.assertEqual(expected_sections, organisation_page_sections)

    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.hyperlink_external_link"
    )
    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.hyperlink_wiki_page"
    )
    def test_generate_projects_list_table_row(
        self, mocked_hyperlink_wiki, mocked_hyperlink
    ):
        platform_url = "[http://platform.com Platform name]"
        project_wiki_page = "[[project name | project name]]"

        mocked_hyperlink.return_value = platform_url
        mocked_hyperlink_wiki.return_value = project_wiki_page

        expected_new_row = (
            f"\n| {project_wiki_page}\n| {platform_url}\n| "
            f"{self.organisation_data['project']['author']}\n| "
            f"{self.organisation_data['project']['status']}\n|-"
        )
        projects_list_new_row = OrganisationPageService().generate_projects_list_table_row(
            self.organisation_data
        )
        self.assertEqual(expected_new_row, projects_list_new_row)

    @patch("server.services.wiki.pages.organisation_service.MediaWikiService")
    @patch(
        "server.services.wiki.pages.organisation_service.WikiTableService.add_table_row"
    )
    def test_create_page(self, mocked_table_row, mocked_mediawiki):
        token = "token example"
        mocked_mediawiki.return_value.get_token.return_value = token

        text_with_table = (
            "=Section=\nSection text\n"
            "==Table Section==\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | Column header\n'
            "|-\n"
            "| Column data\n"
            "|-\n"
            "|}"
        )
        mocked_table_row.return_value = text_with_table

        page_path = (
            f"{self.templates.oeg_page}/{self.document_data['organisation']['name']}"
        )

        OrganisationPageService().create_page(self.document_data)
        mocked_mediawiki.return_value.create_page.assert_called_with(
            token, page_path, text_with_table
        )
