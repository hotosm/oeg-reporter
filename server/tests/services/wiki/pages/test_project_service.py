from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.wiki.pages.project_service import ProjectPageService
from server.models.serializers.document import DocumentSchema


class TestProjectService(BaseTestCase):
    def setUp(self):
        self.document_data = utils.document_data
        self.project_data = DocumentSchema().load(
            partial=True,
            data={
                "project": {
                    "name": self.document_data["project"]["name"],
                    "shortDescription": self.document_data["project"][
                        "shortDescription"
                    ],
                    "created": self.document_data["project"]["created"],
                    "changesetComment": self.document_data["project"][
                        "changesetComment"
                    ],
                    "externalSource": {
                        "instructions": self.document_data["project"]["externalSource"][
                            "instructions"
                        ],
                        "perTaskInstructions": self.document_data["project"][
                            "externalSource"
                        ]["perTaskInstructions"],
                        "imagery": self.document_data["project"]["externalSource"][
                            "imagery"
                        ],
                        "license": self.document_data["project"]["externalSource"][
                            "license"
                        ],
                    },
                    "url": self.document_data["project"]["url"],
                    "users": self.document_data["project"]["users"],
                }
            },
        )
        self.templates = utils.ProjectPageTemplates()

    def test_filter_page_data(self):
        project_page_data = ProjectPageService().filter_page_data(self.document_data)
        project_is_subset = set(project_page_data.keys()).issubset(
            self.document_data.keys()
        )
        self.assertTrue(project_is_subset)

    @patch(
        "server.services.wiki.pages.organisation_service."
        "WikiTextService.format_date_text"
    )
    def test_generate_page_sections_dict(self, mocked_format_date):
        created_date = "30 July 2020"
        mocked_format_date.return_value = created_date

        project_external_source = self.project_data["project"]["external_source"]
        timeframe = f"\n* '''Start Date:''' {created_date}\n"
        hashtag = self.project_data["project"]["changeset_comment"].replace(
            "#", "<nowiki>#</nowiki>"
        )

        expected_sections = {
            self.templates.short_description_section: (
                f"\n{self.project_data['project']['short_description']}\n"
            ),
            self.templates.timeframe_section: timeframe,
            self.templates.url_section: (f"\n{self.project_data['project']['url']}\n"),
            self.templates.external_sources_section: {
                self.templates.instructions_section: (
                    f"\n{project_external_source['instructions']}\n"
                ),
                self.templates.per_task_instructions_section: (
                    f"\n{project_external_source['per_task_instructions']}\n"
                ),
                self.templates.imagery_section: (
                    f"\n{project_external_source['imagery'].strip()}\n"
                ),
                self.templates.license_section: (
                    f"\n{project_external_source['license']}\n"
                ),
            },
            self.templates.hashtag_section: f"\n{hashtag}\n",
        }

        project_page_sections = ProjectPageService().generate_page_sections_dict(
            self.project_data
        )
        self.assertEqual(expected_sections, project_page_sections)

    def test_get_project_users_table_rows(self):
        project_users_row = ProjectPageService().get_project_users_table_rows(
            self.document_data
        )
        expected_project_users_row = "\n| 1\n| user name example\n|-"
        self.assertEqual(expected_project_users_row, project_users_row)

    @patch("server.services.wiki.pages.project_service.MediaWikiService")
    @patch("server.services.wiki.pages.project_service.WikiTableService.add_table_row")
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

        page_path = self.document_data["project"]["name"]

        ProjectPageService().create_page(self.document_data)
        mocked_mediawiki.return_value.create_page.assert_called_with(
            token=token, page_title=page_path, page_text=text_with_table
        )
