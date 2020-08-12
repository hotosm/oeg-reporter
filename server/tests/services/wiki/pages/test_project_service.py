from datetime import datetime
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
            token=token, page_title=page_path.capitalize(), page_text=text_with_table
        )

    def test_get_project_users(self):
        user_id = 1
        user_name = "userName"
        table_text = (
            '{|class="wikitable sortable"\n'
            "|-\n"
            '! scope="col" | OSM ID\n'
            '! scope="col" | Name\n'
            "|-\n"
            f"|  {user_id}\n"
            f"|  {user_name}\n"
            "|-\n"
            "|}\n"
        )
        expected_project_users = [{"userId": "1", "userName": "userName"}]
        project_users = ProjectPageService().get_project_users(table_text)
        self.assertListEqual(expected_project_users, project_users)

    def test_get_date_from_timeframe(self):
        date = datetime.strptime("01/01/2020", "%d/%m/%Y")
        start_date = date.strftime("%m %B %Y")

        timeframe_text = f"* '''Start Date:''' {start_date}"
        timeframe_date = ProjectPageService().get_date_from_timeframe(timeframe_text)
        self.assertIsInstance(timeframe_date, str)

        expected_parsed_date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(expected_parsed_date, timeframe_date)

    def test_get_url_and_id_from_project_url(self):
        project_id = 1
        project_url = f"http://tasks.hotosm.org/projects/{project_id}"

        expected_url_and_id = (project_url, project_id)
        url_and_id = ProjectPageService().get_url_and_id_from_project_url(project_url)
        self.assertTupleEqual(expected_url_and_id, url_and_id)

    def test_get_parsed_hashtag(self):
        wikitext_hashtag = "<nowiki>#</nowiki>tm-project-1"
        parsed_hashtag = ProjectPageService().get_parsed_hashtag(wikitext_hashtag)

        expected_parsed_hashtag = "#tm-project-1"

        self.assertEqual(expected_parsed_hashtag, parsed_hashtag)

    @patch("server.services.wiki.pages.project_service." "MediaWikiService")
    @patch("server.services.wiki.wiki_table_service." "WikiTableService.add_table_row")
    def test_edit_page(self, mocked_edited_page_text, mocked_mediawiki):
        updated_license = "updated license"
        update_fields = {"project": {"externalSource": {"license": updated_license}}}
        updated_project_page_data = {
            "project": {
                "projectId": self.document_data["project"]["projectId"],
                "name": self.document_data["project"]["name"],
                "shortDescription": self.document_data["project"]["shortDescription"],
                "created": self.document_data["project"]["created"],
                "changesetComment": self.document_data["project"]["changesetComment"],
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
                    "license": updated_license,
                },
                "url": self.document_data["project"]["url"],
                "users": self.document_data["project"]["users"],
            }
        }

        current_project_page_data = {
            "project": {"name": self.document_data["project"]["name"]}
        }

        mocked_mediawiki.return_value.get_token.return_value = "token example"
        updated_text = "Updated text"
        mocked_edited_page_text.return_value = updated_text

        ProjectPageService().edit_page(
            updated_project_page_data, update_fields, current_project_page_data
        )
        mocked_mediawiki.return_value.edit_page.assert_called_once_with(
            "token example",
            self.document_data["project"]["name"].capitalize(),
            updated_text,
        )

    @patch("server.services.wiki.pages.project_service." "MediaWikiService")
    @patch("server.services.wiki.wiki_table_service." "WikiTableService.add_table_row")
    def test_edit_page_move_project_page(
        self, mocked_edited_page_text, mocked_mediawiki
    ):
        updated_project_name = "updated project name"
        update_fields = {"project": {"name": updated_project_name}}
        updated_project_page_data = {
            "project": {
                "projectId": self.document_data["project"]["projectId"],
                "name": updated_project_name,
                "shortDescription": self.document_data["project"]["shortDescription"],
                "created": self.document_data["project"]["created"],
                "changesetComment": self.document_data["project"]["changesetComment"],
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
        }

        current_project_name = "project name"
        current_project_page_data = {"project": {"name": current_project_name}}

        mocked_mediawiki.return_value.get_token.return_value = "token example"
        updated_text = "Updated text"
        mocked_edited_page_text.return_value = updated_text

        ProjectPageService().edit_page(
            updated_project_page_data, update_fields, current_project_page_data
        )

        mocked_mediawiki.return_value.move_page.assert_called_once_with(
            token="token example",
            old_page=current_project_name.capitalize(),
            new_page=updated_project_name.capitalize(),
        )
        mocked_mediawiki.return_value.edit_page.assert_called_once_with(
            "token example", updated_project_name.capitalize(), updated_text
        )

    def test_parse_page_to_serializer(self):
        project_serialized_fields = ProjectPageService().parse_page_to_serializer(
            self.templates.page_dictionary, "project name example"
        )

        expected_serialized_fields = {
            "project": {
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
                "name": self.document_data["project"]["name"].capitalize(),
                "shortDescription": self.document_data["project"]["shortDescription"],
                "created": self.document_data["project"]["created"],
                "changesetComment": f'#{self.document_data["project"]["changesetComment"]}',
                "url": f'{self.document_data["project"]["url"]}/projects/{self.document_data["project"]["projectId"]}',
                "projectId": self.document_data["project"]["projectId"],
                "users": [{"userName": "user name example", "userId": "1"}],
            }
        }
        self.assertEqual(project_serialized_fields, expected_serialized_fields)
