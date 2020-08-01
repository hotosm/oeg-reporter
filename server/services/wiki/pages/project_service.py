from server.services.wiki.pages.templates import ProjectPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService


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

    def get_project_users_table_rows(self, project_page_data):
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
        wikitext = WikiTextService()
        mediawiki = MediaWikiService()

        token = mediawiki.get_token()

        project_page_sections = self.document_to_page_sections(document_data)

        sections_text = wikitext.generate_text_from_dict(
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

        mediawiki.create_page(
            token=token,
            page_title=document_data["project"]["name"],
            page_text=updated_text,
        )
