from unittest.mock import patch
from copy import deepcopy

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

        page_path = f"{self.templates.oeg_page}/{self.document_data['organisation']['name'].capitalize()}"

        OrganisationPageService().create_page(self.document_data)
        mocked_mediawiki.return_value.create_page.assert_called_with(
            token, page_path, text_with_table
        )

    def test_parse_page_to_serializer(self):
        organisation_serialized_fields = OrganisationPageService().parse_page_to_serializer(
            self.templates.page_dictionary
        )

        expected_serialized_fields = self.document_data.copy()
        expected_serialized_fields["project"] = [
            {
                "name": self.document_data["project"]["name"],
                "author": self.document_data["project"]["author"],
                "status": self.document_data["project"]["status"],
            }
        ]
        self.assertDictEqual(expected_serialized_fields, organisation_serialized_fields)

    @patch("server.services.wiki.pages.organisation_service." "MediaWikiService")
    def test_edit_page_text(self, mocked_mediawiki):
        updated_project_name = "updated project name"
        update_fields = {"project": {"name": updated_project_name}}
        updated_organisation_page_data = deepcopy(self.document_data)
        updated_organisation_page_data["project"]["name"] = updated_project_name

        projects_list_table = (
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | Name\n'
            "|-\n"
            "| [[Project name example | Project name example]]\n"
            "|-\n"
            "|}\n"
        )
        mocked_mediawiki.return_value.get_page_text.return_value = (
            f"{self.templates.page_initial_section}\n"
            f"=={self.templates.projects_list_section}==\n"
            f"{projects_list_table}"
        )
        edited_page_text = OrganisationPageService().get_edit_page_text(
            update_fields, self.document_data, updated_organisation_page_data
        )
        mocked_mediawiki.return_value.get_page_text.assert_called_with(
            f"{self.templates.oeg_page}/{self.document_data['organisation']['name'].capitalize()}"
        )

        expected_updated_page_text = (
            f"{self.templates.page_initial_section}\n\n"
            f"=={self.templates.projects_section}==\n==={self.templates.projects_list_section}===\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | Name\n'
            "|-\n"
            f"| [[{updated_project_name.capitalize()} | {updated_project_name.capitalize()}]]\n"
            "|-\n"
            "|}"
        )
        self.assertEqual(edited_page_text, expected_updated_page_text)

    @patch("server.services.wiki.pages.organisation_service." "MediaWikiService")
    @patch(
        "server.services.wiki.pages.organisation_service."
        "OrganisationPageService.get_edit_page_text"
    )
    def test_edit_page(self, mocked_edited_page_text, mocked_mediawiki):
        updated_platform_name = "updated platform name"
        update_fields = {"platform": {"name": updated_platform_name}}
        updated_organisation_page_data = {"platform": {"name": updated_platform_name}}
        current_platform_name = "platform name"
        current_organisation_name = "organisation name"
        current_organisation_page_data = {
            "organisation": {"name": current_organisation_name},
            "platform": {"name": current_platform_name},
        }

        mocked_mediawiki.return_value.get_token.return_value = "token example"

        updated_text = "Updated text"
        mocked_edited_page_text.return_value = updated_text

        OrganisationPageService().edit_page(
            updated_organisation_page_data,
            update_fields,
            current_organisation_page_data,
        )
        mocked_mediawiki.return_value.edit_page.assert_called_once_with(
            "token example",
            f"{self.templates.oeg_page}/{current_organisation_name.capitalize()}",
            updated_text,
        )

    @patch("server.services.wiki.pages.organisation_service." "MediaWikiService")
    @patch(
        "server.services.wiki.pages.organisation_service."
        "OrganisationPageService.get_edit_page_text"
    )
    def test_edit_page_move_organisation_page(
        self, mocked_edited_page_text, mocked_mediawiki
    ):
        updated_organisation_name = "updated organisation name"
        update_fields = {"organisation": {"name": updated_organisation_name}}
        updated_organisation_page_data = {
            "organisation": {"name": updated_organisation_name}
        }
        current_organisation_name = "organisation name"
        current_organisation_page_data = {
            "organisation": {"name": current_organisation_name}
        }

        mocked_mediawiki.return_value.get_token.return_value = "token example"

        updated_text = "Updated text"
        mocked_edited_page_text.return_value = updated_text

        OrganisationPageService().edit_page(
            updated_organisation_page_data,
            update_fields,
            current_organisation_page_data,
        )

        mocked_mediawiki.return_value.move_page.assert_called_once_with(
            token="token example",
            old_page=f"{self.templates.oeg_page}/{current_organisation_name.capitalize()}",
            new_page=f"{self.templates.oeg_page}/{updated_organisation_name.capitalize()}",
        )
        mocked_mediawiki.return_value.edit_page.assert_called_once_with(
            "token example",
            f"{self.templates.oeg_page}/{updated_organisation_name.capitalize()}",
            updated_text,
        )

    def test_project_table_field_updated(self):
        update_fields = {"project": {"name": "updated project name"}}
        organisation_page_data = {"project": {"name": "project name"}}
        expected_table_field_updated = "[[Project name | Project name]]"
        table_field_updated = OrganisationPageService().table_field_updated(
            update_fields, organisation_page_data
        )
        self.assertEqual(expected_table_field_updated, table_field_updated)

    def test_platform_table_field_updated(self):
        update_fields = {"platform": {"url": "http://www.updatedexample.com"}}
        organisation_page_data = {
            "platform": {"name": "platform name", "url": "http://www.example.com"}
        }
        expected_table_field_updated = "[http://www.example.com platform name]"
        table_field_updated = OrganisationPageService().table_field_updated(
            update_fields, organisation_page_data
        )
        self.assertEqual(expected_table_field_updated, table_field_updated)

    def test_table_field_not_updated(self):
        update_fields = {"organisation": {"name": "updated organisation name"}}
        organisation_page_data = {
            "platform": {"name": "platform name", "url": "http://www.example.com"}
        }
        is_table_field_updated = OrganisationPageService().table_field_updated(
            update_fields, organisation_page_data
        )
        self.assertFalse(is_table_field_updated)
