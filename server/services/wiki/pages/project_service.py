import re
from datetime import datetime

from server.services.wiki.pages.templates import ProjectPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService
from server.models.serializers.document import DocumentSchema


class ProjectPageService(PageService):
    def __init__(self):
        self.templates = ProjectPageTemplates()
        self.page_fields = [
            "project.name",
            "project.short_description",
            "project.created",
            "project.changeset_comment",
            "project.external_source.instructions",
            "project.external_source.per_task_instructions",
            "project.external_source.imagery",
            "project.external_source.license",
            "project.url",
            "project.project_id",
            "project.users",
        ]

    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the project page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        project_page_data -- Dict containing only the required data
                             for the project page
        """
        project_page_data = {
            "project": {
                "projectId": document_data["project"]["projectId"],
                "name": document_data["project"]["name"],
                "shortDescription": document_data["project"]["shortDescription"],
                "created": document_data["project"]["created"],
                "changesetComment": document_data["project"]["changesetComment"],
                "externalSource": {
                    "instructions": document_data["project"]["externalSource"][
                        "instructions"
                    ],
                    "perTaskInstructions": document_data["project"]["externalSource"][
                        "perTaskInstructions"
                    ],
                    "imagery": document_data["project"]["externalSource"]["imagery"],
                    "license": document_data["project"]["externalSource"]["license"],
                },
                "url": document_data["project"]["url"],
                "users": document_data["project"]["users"],
            }
        }
        return project_page_data

    def generate_page_sections_dict(self, project_page_data: dict):
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in the project page

        Keyword arguments:
        project_page_data -- Dictionary containing the required data for the
                              project page sections

        Returns:
        project_page_sections -- Dictionary with the document content
                                 parsed to wikitext for the project
                                 page sections
        """
        created_date = WikiTextService().format_date_text(
            project_page_data["project"]["created"]
        )
        timeframe = f"\n* '''Start Date:''' {created_date}\n"
        hashtag = project_page_data["project"]["changeset_comment"].replace(
            "#", "<nowiki>#</nowiki>"
        )
        project_external_source = project_page_data["project"]["external_source"]

        project_page_sections = {
            self.templates.short_description_section: (
                f"\n{project_page_data['project']['short_description']}\n"
            ),
            self.templates.timeframe_section: timeframe,
            self.templates.url_section: (f"\n{project_page_data['project']['url']}\n"),
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
        return project_page_sections

    def get_project_users_table_rows(self, project_page_data: dict):
        users = project_page_data["project"]["users"]
        project_users = ""
        for user in users:
            project_users += f"\n| {user['userId']}\n| {user['userName']}\n|-"
        return project_users

    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        mediawiki = MediaWikiService()

        token = mediawiki.get_token()

        project_page_sections = self.document_to_page_sections(document_data)

        sections_text = WikiTextService().generate_text_from_dict(
            self.templates.page_template,
            f"=={self.templates.page_initial_section}==",
            project_page_sections,
        )
        updated_text = WikiTableService().add_table_row(
            page_text=sections_text,
            new_row=self.get_project_users_table_rows(document_data),
            table_section_title=self.templates.team_user_section,
            table_template=self.templates.table_template,
        )

        page_title = (
            f"{self.templates.oeg_page}/Projects/"
            f'{document_data["project"]["name"].capitalize()}'
        )
        if mediawiki.is_existing_page(page_title):
            raise ValueError(
                "Error reporting project "
                f"'{document_data['project']['name'].capitalize()}'."
                " Project already was reported."
            )
        else:
            mediawiki.create_page(
                token=token, page_title=page_title, page_text=updated_text,
            )

    def edit_page(
        self, document_data: dict, update_fields: dict, project_page_data: dict
    ):
        """
        Edits a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        mediawiki = MediaWikiService()
        token = mediawiki.get_token()
        page_title = (
            f"{self.templates.oeg_page}/Projects/"
            f'{project_page_data["project"]["name"].capitalize()}'
        )

        project_page_sections = self.document_to_page_sections(document_data)

        sections_text = WikiTextService().generate_text_from_dict(
            self.templates.page_template,
            f"=={self.templates.page_initial_section}==",
            project_page_sections,
        )
        updated_text = WikiTableService().add_table_row(
            page_text=sections_text,
            new_row=self.get_project_users_table_rows(document_data),
            table_section_title=self.templates.team_user_section,
            table_template=self.templates.table_template,
        )

        if (
            "project" in update_fields.keys()
            and "name" in update_fields["project"].keys()
            and update_fields["project"]["name"].capitalize()
            != project_page_data["project"]["name"].capitalize()
        ):
            new_page = (
                f"{self.templates.oeg_page}/Projects/"
                f'{document_data["project"]["name"].capitalize()}'
            )
            mediawiki.move_page(token=token, old_page=page_title, new_page=new_page)
            mediawiki.edit_page(token, new_page, updated_text)
        else:
            mediawiki.edit_page(token, page_title, updated_text)

    def parse_page_to_serializer(self, page_dictionary: dict, project_name: str):
        project_page_data = {"project": {"externalSource": {}}}

        project_page_data["project"]["name"] = project_name.capitalize()

        project_page_data["project"]["shortDescription"] = page_dictionary[
            self.templates.project_section
        ][self.templates.short_description_section].replace("\n", "")

        project_page_data["project"]["created"] = self.get_date_from_timeframe(
            page_dictionary[self.templates.project_section][
                self.templates.timeframe_section
            ].replace("\n", "")
        )
        project_page_data["project"]["changesetComment"] = self.get_parsed_hashtag(
            page_dictionary[self.templates.project_section][
                self.templates.hashtag_section
            ].replace("\n", "")
        )

        project_url, project_id = self.get_url_and_id_from_project_url(
            page_dictionary[self.templates.project_section][
                self.templates.url_section
            ].replace("\n", "")
        )
        project_page_data["project"]["url"] = project_url
        project_page_data["project"]["projectId"] = project_id

        project_page_data["project"]["externalSource"][
            "instructions"
        ] = page_dictionary[self.templates.external_sources_section][
            self.templates.instructions_section
        ].replace(
            "\n", ""
        )
        project_page_data["project"]["externalSource"][
            "perTaskInstructions"
        ] = page_dictionary[self.templates.external_sources_section][
            self.templates.per_task_instructions_section
        ].replace(
            "\n", ""
        )
        project_page_data["project"]["externalSource"]["imagery"] = page_dictionary[
            self.templates.external_sources_section
        ][self.templates.imagery_section].replace("\n", "")
        project_page_data["project"]["externalSource"]["license"] = page_dictionary[
            self.templates.external_sources_section
        ][self.templates.license_section].replace("\n", "")

        project_page_data["project"]["users"] = self.get_project_users(
            page_dictionary[self.templates.team_user_section][
                self.templates.users_list_section
            ]
        )
        # validate
        document_schema = DocumentSchema(partial=True, only=self.page_fields)
        document_schema.load(project_page_data)
        return project_page_data

    def get_project_users(self, table_text: str):
        users_list_table = WikiTableService().get_text_table(table_text)
        users_list_data = users_list_table.data(span=False)
        users_list = []

        for table_row_number, table_row_data in enumerate(users_list_data[1:], start=1):
            user_id = users_list_table.cells(
                row=table_row_number, column=self.templates.users_list_user_id_column
            ).value

            user_name = users_list_table.cells(
                row=table_row_number, column=self.templates.users_list_user_name_column
            ).value
            users_list.append(
                {"userId": user_id.strip(), "userName": user_name.strip()}
            )
        return users_list

    def get_date_from_timeframe(self, timeframe_text: str):
        date = re.search(r"\d{2}\s\w+\s\d{4}", timeframe_text)
        parsed_date = datetime.strptime(date.group(), "%m %B %Y").strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return parsed_date

    def get_url_and_id_from_project_url(self, url_text: str):
        project_url = url_text
        project_id = int(url_text.split("/projects/")[-1])
        return project_url, project_id

    def get_parsed_hashtag(self, hashtag_text: str):
        hashtag = "#" + hashtag_text.split("</nowiki>")[-1]
        return hashtag
