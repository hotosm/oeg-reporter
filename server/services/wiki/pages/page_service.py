from abc import ABC, abstractmethod

from server.models.serializers.document import DocumentSchema
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_section_service import WikiSectionService


class PageService(ABC):
    def document_to_page_sections(self, document_data: dict) -> dict:
        """
        Generate dict containing the document content
        parsed to wikitext for all sections present
        in a page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        page_sections_data -- Dictionary containing the document
                              content parsed to wikitext
                              for all page sections
        """
        # Filter page data from document data
        page_data = self.filter_page_data(document_data)

        # Serialize document with page content
        document_schema = DocumentSchema(only=self.page_fields)
        serialized_page_data = document_schema.load(page_data)

        # Generate page sections dictionary
        page_sections_data = self.generate_page_sections_dict(serialized_page_data)
        return page_sections_data

    def wikitext_to_dict(self, page_title: str):
        mediawiki = MediaWikiService()
        text = mediawiki.get_page_text(page_title)

        redirect_page = MediaWikiService().is_redirect_page(text)
        if redirect_page:
            raise ValueError(
                f"Error getting text from the page '{page_title}'."
                f" Page was moved from '{page_title}' to '{redirect_page}'"
            )
        else:
            sections = WikiSectionService().get_sections(text)
            page_sections_dict = self.generate_sections_dict(sections)
            if not page_sections_dict:
                raise ValueError(f"Error parsing page '{page_title}' to dict")
            else:
                return page_sections_dict

    def generate_sections_dict(self, sections):
        page_sections_dict = {}
        for section in sections:
            if section.title is not None:

                try:
                    parent_section_level = 2
                    (
                        start_index,
                        end_index,
                    ) = WikiSectionService().get_section_title_str_index(
                        section, section.string, parent_section_level
                    )
                except ValueError:
                    continue

                parent_section_text = section.string[
                    end_index : len(section.string)  # noqa
                ]
                children_sections = WikiSectionService().get_sections(
                    parent_section_text
                )
                children_dict = {}
                for child_section in children_sections:
                    if child_section.title is not None:

                        (
                            child_start_index,
                            child_end_index,
                        ) = WikiSectionService().get_section_title_str_index(
                            child_section,
                            child_section.string,
                            parent_section_level + 1,
                        )
                        children_dict[child_section.title] = child_section.string[
                            child_end_index : len(child_section.string)  # noqa
                        ]
                        page_sections_dict[section.title] = children_dict
        return page_sections_dict

    @abstractmethod
    def filter_page_data(self, document_data: dict) -> dict:
        """
        Filter required data for a specific page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines

        Returns:
        dict -- Dict containing only the required data
        for a specific page
        """

    @abstractmethod
    def generate_page_sections_dict(self, serialized_page_data: dict) -> dict:
        """
        Generate dict containing the document content parsed to wikitext
        for all sections present in a page

        Keyword arguments:
        serialized_page_data -- Dictionary containing the required data for the
                                page sections

        Returns:
        dict -- Dictionary with the document content parsed to wikitext
                for all sections present in a page
        """

    @abstractmethod
    def create_page(self, document_data: dict) -> None:
        """
        Creates a wiki page

        Keyword arguments:
        document_data -- All required data for a project using
                         Organised Editing Guidelines
        """
