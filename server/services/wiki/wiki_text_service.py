from datetime import datetime

from flask import current_app

from server.services.wiki.wiki_section_service import WikiSectionService


class WikiTextService:
    def generate_text_from_dict(
        self, template_text: str, page_initial_section: str, page_data: dict
    ):
        """
        Generates text from dict

        Keyword Arguments:
        template_text -- Text used as template
        page_initial_section -- The first section of the page
        page_data -- Dict containing data of all page sections

        Returns:
        updated_text -- Text formatted with wikitext syntax
        """
        section_obj = WikiSectionService()
        sections = section_obj.get_sections(template_text)
        updated_text = f"{page_initial_section}\n"

        for section in sections:
            if section_obj.is_section_being_updated(section, page_data):
                start_index, end_index = section_obj.get_section_title_str_index(
                    section, template_text
                )
                page_section_data = page_data[section.title]

                if section_obj.parent_section_contains_child_section(page_section_data):
                    for (children_section_number, child_section) in enumerate(
                        page_section_data
                    ):
                        child_section_title = section_obj.add_child_section_markers(
                            section, child_section
                        )
                        # If the section has more than one child section
                        # this child's section data must be placed after
                        # the predecessor child section
                        if children_section_number > 0:
                            end_index = section_obj.update_child_section_string_position(
                                page_data, section, children_section_number
                            )

                        # Update page text
                        # if child_section != table_section:
                        updated_text += (
                            template_text[start_index:end_index]
                            + child_section_title
                            + page_section_data[child_section]
                        )
                else:
                    # Update page text
                    updated_text += (
                        template_text[start_index:end_index] + page_section_data
                    )
        return updated_text

    def hyperlink_external_link(self, text: str, link: str) -> str:
        """
        Hyperlink an external page to a text

        Keyword arguments:
        text -- The text that will hyperlink to an external page
        link -- The external link that is going to be present in
                text

        Returns:
        hyperlinked_text -- The text with a hyperlink to an
                            external page
        """
        hyperlinked_text = f"[{link} {text}]"
        return hyperlinked_text

    def hyperlink_wiki_page(self, wiki_page: str, text: str) -> str:
        """
        Hyperlink a wiki page to a text

        Keyword arguments:
        text -- The text that will hyperlink to a wiki page
        link -- The wiki page link that is going
                to be present in text

        Returns:
        hyperlinked_page -- The text with a hyperlink to a
                            wiki page
        """
        hyperlinked_page = f"[[{wiki_page} | {text}]]"
        return hyperlinked_page

    def format_date_text(self, date: datetime) -> str:
        """
        Format a date into the format "%dd month_name %YYYY"

        Keyword arguments:
        date -- Date being formatted

        Returns:
        text_date -- Dictionary with result of post request for checking
                the MediaWiki API Token
        """
        try:
            date_month = date.strftime("%B")
            date_day = date.strftime("%d")
            date_year = date.strftime("%Y")

            text_date = f"{date_day} {date_month} {date_year}"
            return text_date
        except AttributeError:
            current_app.logger.debug("Error parsing date")
            raise ValueError("Error parsing date")
