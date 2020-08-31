from collections import namedtuple

import wikitextparser as wtp

from server.tests.base_test_config import BaseTestCase
from server.services.wiki.wiki_section_service import WikiSectionService


class TestWikiSectionService(BaseTestCase):
    def test_section_being_updated(self):
        SectionStub = namedtuple("Section", ["title"])

        section_title = "section title"
        section = SectionStub(section_title)

        page_data = {section_title: "section text"}
        updated_section = WikiSectionService().is_section_being_updated(
            section, page_data
        )
        self.assertTrue(updated_section)

    def test_section_not_being_updated(self):
        SectionStub = namedtuple("Section", ["title"])

        section_title = None
        section = SectionStub(section_title)

        page_data = {section_title: "section text"}
        updated_section = WikiSectionService().is_section_being_updated(
            section, page_data
        )
        self.assertFalse(updated_section)

    def test_section_parent_section_contains_child_section(self):
        page_section_data = {"child section": "child section text"}
        contains_child_section = WikiSectionService().parent_section_contains_child_section(
            page_section_data
        )
        self.assertTrue(contains_child_section)

    def test_section_parent_section_not_contains_child_section(self):
        page_section_data = "parent section text"
        contains_child_section = WikiSectionService().parent_section_contains_child_section(
            page_section_data
        )
        self.assertFalse(contains_child_section)

    def test_add_child_section_markers(self):
        SectionStub = namedtuple("Section", ["level"])
        parent_section_level = 1

        parent_section = SectionStub(parent_section_level)

        child_section_markers = "=" * (parent_section_level + 1)
        child_section_text = "text"
        expected_child_section_title = (
            f"\n{child_section_markers}"
            f"{child_section_text}"
            f"{child_section_markers}"
        )

        child_section_title = WikiSectionService().add_child_section_markers(
            parent_section, child_section_text
        )

        self.assertEqual(expected_child_section_title, child_section_title)

    def test_get_sections(self):
        text = "=Section=\nSection text"
        section_service = WikiSectionService()
        text_sections = section_service.get_sections(text)
        # check if all list items are of Section type
        section_list_instance = all(
            isinstance(section, wtp.Section) for section in text_sections
        )
        self.assertTrue(section_list_instance)

    def test_get_section_index(self):
        text = "=Section=\nSection text\n=Second section="
        expected_section_index = 2
        section_service = WikiSectionService()
        section_index = section_service.get_section_index(text, "Second section")
        self.assertEqual(expected_section_index, section_index)

    def test_get_section_index_fails_with_no_existing_section(self):
        text = "=Section=\nSection text\n=Second section="
        section_service = WikiSectionService()
        with self.assertRaises(ValueError):
            section_service.get_section_index(text, "Non existing section")

    def test_get_section_table(self):
        col_header = "Column header"
        col_data = "Column data"
        text = (
            "=Section=\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            f'! scope="col" | {col_header}\n'
            "|-\n"
            f"| {col_data}\n"
            "|-\n"
            "|}"
        )
        section_service = WikiSectionService()
        section_table = section_service.get_section_table(text, "Section")
        self.assertIsInstance(section_table, wtp.Table)

        # Assert data in table rows
        table_header_data = section_table.data()[0][0]
        table_col_data = section_table.data()[1][0]
        self.assertEqual(col_header, table_header_data)
        self.assertEqual(col_data, table_col_data)

    def test_get_section_table_fails_without_table_in_text(self):
        text_without_table = "=Section title=\nText without table"
        with self.assertRaises(ValueError):
            WikiSectionService().get_section_table(text_without_table, "Section title")

    def test_get_section_title_str_index_fails_with_no_existing_section(self):
        template_text = "=Section=\n" "Section text"
        section = wtp.Section("=Different Section title=\n" "Section text")
        section_level = section.level
        with self.assertRaises(ValueError):
            WikiSectionService().get_section_title_str_index(
                section, template_text, section_level
            )
