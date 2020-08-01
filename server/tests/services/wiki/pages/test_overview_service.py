from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.wiki.pages.overview_service import OverviewPageService


class TestOverviewService(BaseTestCase):
    def setUp(self):
        self.document_data = utils.document_data
        self.overview_data = {
            "organisation": {
                "name": self.document_data["organisation"]["name"],
                "url": self.document_data["organisation"]["url"],
            },
            "platform": {
                "name": self.document_data["platform"]["name"],
                "url": self.document_data["platform"]["url"],
            },
        }
        self.templates = utils.OverviewPageTemplates()

    def test_filter_page_data(self):
        overview_page_data = OverviewPageService().filter_page_data(self.document_data)
        overview_is_subset = set(overview_page_data.keys()).issubset(
            self.document_data.keys()
        )
        self.assertTrue(overview_is_subset)

    @patch(
        "server.services.wiki.pages.overview_service."
        "OverviewPageService.generate_activities_list_table_row"
    )
    def test_generate_page_sections_dict(self, mocked_row):
        new_row = (
            "\n| [[Organised_Editing/Activities/OrganisationName | "
            "Organisation name]]\n| [http://www.platform.com/ "
            "Platform name]\n|-"
        )
        mocked_row.return_value = new_row

        expected_sections = {self.templates.activities_list_section_title: new_row}

        overview_page_sections = OverviewPageService().generate_page_sections_dict(
            self.overview_data
        )
        mocked_row.assert_called_with(self.overview_data)
        self.assertEqual(expected_sections, overview_page_sections)

    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.hyperlink_external_link"
    )
    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.hyperlink_wiki_page"
    )
    def test_generate_activities_list_table_row(
        self, mocked_hyperlink_wiki, mocked_hyperlink
    ):
        platform_url = "[http://platform.com Platform name]"
        organisation_wiki_page = "[[organisation name | organisation name]]"

        mocked_hyperlink.return_value = platform_url
        mocked_hyperlink_wiki.return_value = organisation_wiki_page

        expected_new_row = f"\n| {organisation_wiki_page}\n| {platform_url}\n|-"
        activities_list_row = OverviewPageService().generate_activities_list_table_row(
            self.overview_data
        )
        self.assertEqual(expected_new_row, activities_list_row)

    @patch("server.services.wiki.pages.overview_service.MediaWikiService")
    @patch("server.services.wiki.pages.overview_service.WikiTableService.add_table_row")
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

        page_path = self.templates.oeg_page

        OverviewPageService().create_page(self.document_data)
        mocked_mediawiki.return_value.create_page.assert_called_with(
            token, page_path, text_with_table
        )
