from abc import ABC, abstractmethod

from server.models.serializers.document import DocumentSchema


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
