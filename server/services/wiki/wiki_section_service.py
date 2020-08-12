import re

import wikitextparser as wtp


class WikiSectionService:
    def get_sections(self, text: str) -> list:
        """
        Returns a list with all sections in a string
        formatted in wikitext

        Keyword arguments:
        text -- The text which the sections are
                 being searched

        Returns:
        sections -- list with all sections
        """
        wtp_text = wtp.parse(text)
        sections = wtp_text.sections
        return sections

    def get_section_index(self, text, section_title: str) -> int:
        """
        Get the index of a section in a wiki page

        Keyword arguments:
        section_title -- the title of the section
                         in which the index is searched

        Raises:
        ValueError -- Exception raised when handling wiki

        Returns:
        index -- The index of the section
        """
        sections = self.get_sections(text)
        for index, section in enumerate(sections):
            if section.title is not None and section.title == section_title:
                return index
        raise ValueError(
            f"Error getting section '{section_title}' index." " Section doesn't exist"
        )

    def get_section_table(self, text: str, section_title: str) -> wtp.Table:
        """
        Get the first table of a section in a wiki page

        Keyword arguments:
        text -- The text of a wiki page
        section_title -- the title of the section
                         in which the index is searched

        Raises:
        WikiServiceError -- Exception raised when handling wiki

        Returns:
        index -- The index of the section
        """
        try:
            section = self.get_section_index(text, section_title)
            sections = self.get_sections(text)
            table = sections[section].get_tables()[0]
            return table
        except IndexError:
            raise ValueError(
                f"Error getting table from section '{section_title}'."
                " Section does not contain a table"
            )

    def get_section_title_str_index(
        self, section: wtp.Section, template_text: str, section_level: int
    ) -> tuple:
        """
        Get the starting and ending position of
        a section's title string

        Keyword arguments:
        section -- The section which the index is being searched
        template_text -- The section text template
        section_level -- Integer representing the section level

        Returns:
        start_end_index,end_index -- The starting and ending position of
                                     a section's title string
        """
        section_title_string = re.search(
            f"(=){{{section_level}}}({section.title})(=){{{section_level}}}",
            template_text,
        )
        if section_title_string is None:
            raise ValueError(f"Error getting section '{section.title}' index.")
        start_index = section_title_string.span()[0]
        end_index = section_title_string.span()[1]
        return start_index, end_index

    def add_child_section_markers(
        self, parent_section: wtp.Section, child_section: str
    ) -> str:
        """
        Parse text from child section by adding section
        markers according to parent section level

        Keyword arguments:
        parent_section -- The parent section
        child_section -- The text of the child section

        Returns:
        child_section_title -- The parsed text of the child section
        """
        child_section_markers = "=" * (parent_section.level + 1)
        child_section_title = (
            f"\n{child_section_markers}" f"{child_section}" f"{child_section_markers}"
        )
        return child_section_title

    def update_child_section_string_position(
        self, page_data: dict, section: wtp.Section, child_section_index: int
    ) -> int:
        """
        Updates the position of the string in which the child section is
        going to be added for right after the predecessor
        child section, instead of adding it right after the
        parent section title

        Keyword arguments:
        page_data -- Dict containing the data for a page
        child_section_index -- Index indicating the position
                               in which the child section should
                               be added in the text of the page

        Returns:
        new_end_index -- The parsed text of the children section
        """
        children_section_keys = list(page_data[section.title].keys())
        predecessor_child_section_title = children_section_keys[child_section_index - 1]
        new_end_index = len(predecessor_child_section_title)
        return new_end_index

    def parent_section_contains_child_section(self, page_section_data):
        """
        Check if the section contains child section

        Keyword arguments:
        page_section_data -- The page section data

        Returns:
        bool -- Boolean indicating if the section contains child section
        """
        if isinstance(page_section_data, dict):
            return True
        else:
            return False

    def is_section_being_updated(self, section: wtp.Section, page_data: dict) -> bool:
        """
        Check if the section is being updated or if it is
        just a section title

        Keyword arguments:
        section -- The section being checked
        page_data -- Dict containing the data for a page

        Returns:
        bool -- Boolean indicating if the section is being updated
        """
        if section.title is not None and section.title in list(page_data.keys()):
            return True
        else:
            return False
