from server.services.wiki.pages.templates import OverviewPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService


class OverviewPageService(PageService):
    def __init__(self):
        self.templates = OverviewPageTemplates()
        self.page_fields = [
            "organisation.name",
            "organisation.url",
            "platform.name",
            "platform.url",
        ]

    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for the overview page from
        document data

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        overview_page_data -- Dict containing only the required data
                              for the overview page
        """
        overview_page_data = {
            "organisation": {
                "name": document_data["organisation"]["name"],
                "url": document_data["organisation"]["url"],
            },
            "platform": {
                "name": document_data["platform"]["name"],
                "url": document_data["platform"]["url"],
            },
        }
        return overview_page_data

    def generate_page_sections_dict(self, overview_page_data: dict) -> dict:
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in the overview page

        Keyword arguments:
        overview_page_data -- Dictionary containing the required data for the
                              overview page sections

        Returns:
        overview_page_sections -- Dictionary with the document content
                                  parsed to wikitext for the overview
                                  page sections
        """
        new_row = self.generate_activities_list_table_row(overview_page_data)
        activities_list_section = self.templates.activities_list_section_title

        overview_page_sections = {activities_list_section: new_row}
        return overview_page_sections

    def generate_activities_list_table_row(self, overview_page_data: dict) -> str:
        """
        Generates a new table row for activities list table

        overview_page_data -- Dict containing only the required data
                              for the overview page

        Returns:
        new_row -- String in wikitext format for a new table row
        """
        wikitext = WikiTextService()

        organisation_name = overview_page_data["organisation"]["name"]
        organisation_page_path = f"{self.templates.oeg_page}/" f"{organisation_name}"

        organisation_link = wikitext.hyperlink_wiki_page(
            organisation_page_path, organisation_name
        )

        platform_link = wikitext.hyperlink_external_link(
            overview_page_data["platform"]["name"],
            overview_page_data["platform"]["url"],
        )

        new_row = f"\n| {organisation_link}\n| {platform_link}\n|-"
        return new_row

    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
        mediawiki = MediaWikiService()
        wikitext = WikiTextService()
        token = mediawiki.get_token()

        page_title = self.templates.oeg_page

        overview_page_sections = self.document_to_page_sections(document_data)

        sections_text = wikitext.generate_text_from_dict(
            self.templates.page_template,
            self.templates.page_initial_section,
            overview_page_sections,
        )
        updated_text = WikiTableService().add_table_row(
            page_text=sections_text,
            new_row=self.generate_activities_list_table_row(document_data),
            table_section_title=self.templates.activities_list_section_title,
            table_template=self.templates.table_template,
        )
        mediawiki.create_page(token, page_title, updated_text)
