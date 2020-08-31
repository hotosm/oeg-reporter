from copy import deepcopy
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
        mocked_mediawiki.return_value.is_existing_page.return_value = True

        organisation_name = self.document_data["organisation"]["name"]
        platform_name = self.document_data["platform"]["name"]

        text_with_table = (
            "==Activities==\n"
            "===Activities list===\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            "! scope='col' | Organisation\n"
            "! scope='col' | Platform\n"
            "|-\n"
            f"| [[Organised_Editing/Activities/Auto_report/{organisation_name} | {organisation_name}]]\n"
            f"| [https://tasks-stage.hotosm.org/ {platform_name}]\n"
            "|-\n"
            "|}\n"
        )
        mocked_table_row.return_value = text_with_table
        mocked_mediawiki.return_value.get_page_text.return_value = text_with_table

        page_title = self.templates.oeg_page

        OverviewPageService().create_page(self.document_data)
        mocked_mediawiki.return_value.edit_page.assert_called_with(
            token, page_title, text_with_table
        )

    @patch("server.services.wiki.pages.overview_service." "MediaWikiService")
    def test_edit_page_text_update_overview_page_table(self, mocked_mediawiki):
        updated_organisation_name = "updated organisation name"
        update_fields = {"organisation": {"name": updated_organisation_name}}
        updated_overview_page_data = deepcopy(self.document_data)
        updated_overview_page_data["organisation"]["name"] = updated_organisation_name

        organisation_name = self.document_data["organisation"]["name"]
        platform_name = self.document_data["platform"]["name"]

        overview_page_table = (
            "{|class='wikitable sortable'\n"
            "|-\n"
            "! scope='col' | Organisation\n"
            "! scope='col' | Platform\n"
            "|-\n"
            f"| [[Organised_Editing/Activities/Auto_report/{organisation_name.capitalize()}"
            f" | {organisation_name.capitalize()}]]\n"
            f"| [https://tasks-stage.hotosm.org/ {platform_name}]\n"
            "|-\n"
            "|}\n"
        )
        mocked_mediawiki.return_value.get_page_text.return_value = (
            f"\n{self.templates.page_initial_section}\n"
            f"=={self.templates.activities_list_section_title}==\n"
            f"{overview_page_table}"
        )
        edited_page_text = OverviewPageService().edit_page_text(
            update_fields, self.document_data, updated_overview_page_data
        )
        mocked_mediawiki.return_value.get_page_text.assert_called_with(
            self.templates.oeg_page
        )
        expected_updated_page_text = (
            f"\n={self.templates.page_initial_section}=\n"
            f"==={self.templates.activities_list_section_title}===\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            "! scope='col' | Organisation\n"
            "! scope='col' | Platform\n"
            "|-\n"
            f"| [[{self.templates.oeg_page}/{updated_organisation_name.capitalize()} "
            f"| {updated_organisation_name.capitalize()}]]\n"
            f"| [https://tasks-stage.hotosm.org/ {platform_name}]\n"
            "|-\n"
            "|}"
        )
        self.assertEqual(edited_page_text, expected_updated_page_text)

    @patch("server.services.wiki.pages.overview_service." "MediaWikiService")
    def test_edit_page_text(self, mocked_mediawiki):
        updated_project_name = "updated project name"
        update_fields = {"project": {"name": updated_project_name}}
        updated_overview_page_data = deepcopy(self.document_data)
        updated_overview_page_data["project"]["name"] = updated_project_name

        updated_document = deepcopy(self.document_data)
        updated_document["project"]["name"] = updated_project_name

        current_overview_page_data = self.document_data

        overview_page_table = (
            "{|class='wikitable sortable'\n"
            "|-\n"
            "! scope='col' | Organisation\n"
            "|-\n"
            f"| [[{self.templates.oeg_page}/Hot | Hot]]\n"
            "|-\n"
            "|}\n"
        )
        page_text = (
            f"\n{self.templates.page_initial_section}\n"
            f"=={self.templates.activities_list_section_title}==\n"
            f"{overview_page_table}"
        )
        mocked_mediawiki.return_value.get_page_text.return_value = (
            f"\n{self.templates.page_initial_section}\n"
            f"=={self.templates.activities_list_section_title}==\n"
            f"{overview_page_table}"
        )
        edited_page_text = OverviewPageService().edit_page_text(
            update_fields, current_overview_page_data, updated_overview_page_data
        )
        mocked_mediawiki.return_value.get_page_text.assert_called_with(
            self.templates.oeg_page
        )
        self.assertEqual(edited_page_text, page_text)

    @patch("server.services.wiki.pages.overview_service." "MediaWikiService")
    @patch(
        "server.services.wiki.pages.overview_service."
        "OverviewPageService.edit_page_text"
    )
    def test_edit_page(self, mocked_edited_page_text, mocked_mediawiki):
        updated_platform_name = "updated platform name"
        update_fields = {"platform": {"name": updated_platform_name}}
        updated_overview_page_data = {"platform": {"name": updated_platform_name}}
        current_platform_name = "platform name"
        current_organisation_name = "organisation name"
        current_overview_page_data = {
            "organisation": {"name": current_organisation_name},
            "platform": {"name": current_platform_name},
        }

        mocked_mediawiki.return_value.get_token.return_value = "token example"

        updated_text = "Updated text"
        mocked_edited_page_text.return_value = updated_text

        OverviewPageService().edit_page(
            updated_overview_page_data, update_fields, current_overview_page_data
        )
        mocked_mediawiki.return_value.edit_page.assert_called_once_with(
            "token example", f"{self.templates.oeg_page}", updated_text
        )

    def test_parse_page_to_serializer(self):
        overview_serialized_fields = OverviewPageService().parse_page_to_serializer(
            self.templates.page_dictionary
        )
        expected_serialized_fields = {
            "organisation": [{"name": self.document_data["organisation"]["name"]}],
            "platform": [
                {
                    "name": self.document_data["platform"]["name"],
                    "url": self.document_data["platform"]["url"],
                }
            ],
        }
        self.assertDictEqual(expected_serialized_fields, overview_serialized_fields)

    def test_get_overview_page_platforms_and_organisations(self):
        organisation_page_hyperlink = (
            f"[[{self.templates.oeg_page}/organisation | organisation]]"
        )
        platform_hyperlink = "[http://www.platform.com platform name]"
        table_text = (
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | Organisation\n'
            '! scope="col" | Platform\n'
            "|-\n"
            f"| {organisation_page_hyperlink}\n"
            f"| {platform_hyperlink}\n"
            "|-\n"
            "|}\n"
        )
        expected_platforms_and_organisations = (
            [{"name": "platform name", "url": "http://www.platform.com"}],
            [{"name": "organisation"}],
        )
        platforms_and_organisations = OverviewPageService().get_overview_page_platforms_and_organisations(
            table_text
        )
        self.assertTupleEqual(
            expected_platforms_and_organisations, platforms_and_organisations
        )
