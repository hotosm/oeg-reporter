from server.services.wiki.pages.templates import OrganisationPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService


class OrganisationPageService(PageService):
    def __init__(self):
        self.templates = OrganisationPageTemplates()
        self.page_fields = [
            "project.name",
            "project.author",
            "project.status",
            "organisation.name",
            "organisation.description",
            "organisation.url",
            "platform.name",
            "platform.url",
        ]

    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the organisation page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        organisation_page_data -- Dict containing only the required data
                              for the organisation page
        """
        organisation_page_data = {
            "organisation": {
                "name": document_data["organisation"]["name"],
                "description": document_data["organisation"]["description"],
                "url": document_data["organisation"]["url"],
            },
            "project": {
                "name": document_data["project"]["name"],
                "author": document_data["project"]["author"],
                "status": document_data["project"]["status"],
            },
            "platform": {
                "name": document_data["platform"]["name"],
                "url": document_data["platform"]["url"],
            },
        }
        return organisation_page_data

    def generate_page_sections_dict(self, organisation_page_data: dict) -> dict:
        """
        Generate dict containing the document content
        parsed to wikitext for all sections present
        in the organisation page

        Keyword arguments:
        organisation_page_data -- Dictionary containing the
                                  required data for the
                                  organisation page sections

        Returns:
        organisation_page_sections -- Dictionary with the document
                                      content parsed to wikitext
                                      for the organisation page sections
        """
        wikitext = WikiTextService()

        organisation_url = wikitext.hyperlink_external_link(
            organisation_page_data["organisation"]["name"],
            organisation_page_data["organisation"]["url"],
        )

        platform_url = wikitext.hyperlink_external_link(
            organisation_page_data["platform"]["name"],
            organisation_page_data["platform"]["url"],
        )

        organisation_page_sections = {
            self.templates.organisation_section: {
                self.templates.organisation_link_section: f"\n{organisation_url}\n",
                self.templates.organisation_description_section: (
                    f"\n{organisation_page_data['organisation']['description']}\n"
                ),
            },
            self.templates.platform_section: {
                self.templates.platform_link_section: f"\n{platform_url}\n",
            },
        }
        return organisation_page_sections

    def generate_projects_list_table_row(self, organisation_page_data: dict) -> str:
        """
        Generates a new table row for projects list table

        organisation_page_data -- Dict containing only the required data
                                  for the organisation page

        Returns:
        new_row -- String in wikitext format for a new table row
        """
        wikitext = WikiTextService()

        platform_url = wikitext.hyperlink_external_link(
            organisation_page_data["platform"]["name"],
            organisation_page_data["platform"]["url"],
        )

        project_wiki_page = wikitext.hyperlink_wiki_page(
            organisation_page_data["project"]["name"],
            organisation_page_data["project"]["name"],
        )

        new_row = (
            f"\n| {project_wiki_page}\n| {platform_url}\n| "
            f"{organisation_page_data['project']['author']}\n| "
            f"{organisation_page_data['project']['status']}\n|-"
        )
        return new_row

    def create_page(self, document_data: dict):
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        mediawiki = MediaWikiService()

        organisation_page_sections = self.document_to_page_sections(document_data)

        sections_text = WikiTextService().generate_text_from_dict(
            self.templates.page_template,
            self.templates.page_initial_section,
            organisation_page_sections,
        )
        updated_text = WikiTableService().add_table_row(
            page_text=sections_text,
            new_row=self.generate_projects_list_table_row(document_data),
            table_section_title=self.templates.projects_section,
            table_template=self.templates.table_template,
        )

        page_path = f"{self.templates.oeg_page}/{document_data['organisation']['name']}"
        token = mediawiki.get_token()
        mediawiki.create_page(token, page_path, updated_text)
