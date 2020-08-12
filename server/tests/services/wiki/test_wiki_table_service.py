import wikitextparser as wtp

from server.tests.base_test_config import BaseTestCase
from server.services.wiki.wiki_table_service import WikiTableService


class TestWikiTableService(BaseTestCase):
    def test_get_table_column_numbers(self):
        text = wtp.parse(
            """{|
        |  column data  ||   second column data
        |}"""
        )
        col_numbers = WikiTableService().get_table_column_numbers(text.tables[0])
        expected_col_numbers = 2
        self.assertEqual(col_numbers, expected_col_numbers)

    def test_add_table_row(self):
        page_text = "=Section=\n==Child section==\nSection text\n"
        new_table_row = "\n| First column data\n|-"
        table_section_title = "Table section"
        table_template = (
            "==Table section==\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column header\n'
            "|-\n"
            "|}\n"
        )
        text_with_table_row = WikiTableService().add_table_row(
            page_text, new_table_row, table_section_title, table_template
        )

        expected_table = (
            f"{page_text}"
            "==Table section==\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column header\n'
            "|-\n"
            "| First column data\n"
            "|-\n"
            "|}"
        )
        self.assertEqual(expected_table, text_with_table_row)

    def test_get_table_last_column_data(self):
        first_column_data, second_column_data = (" First column", " Second column")
        text = wtp.parse(
            f"""{{|class='wikitable sortable'
        |-
        ! scope="col" |{first_column_data}
        ! scope="col" |{second_column_data}
        |-
        | First column data
        | Second column data
        |-
        |}}"""
        )

        column_numbers = 2
        table_last_column_data = WikiTableService().get_table_last_column_data(
            text.tables[0], column_numbers
        )
        self.assertEqual(second_column_data, table_last_column_data)

    def test_get_new_row_index(self):
        text = wtp.parse(
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column data\n'
            "|-\n"
            "|}\n"
        )
        table_new_row_index = WikiTableService().get_new_row_index(text.tables[0])
        header_delimiter_length = len("\n|-\n")
        expected_new_row_index = len(text) - header_delimiter_length
        self.assertEqual(table_new_row_index, expected_new_row_index)

    def test_edit_table(self):
        edit_row_column_data = "First column data"
        table_section = "\n==Table section=="

        updated_data = "updated data"
        updated_row = f"\n| {updated_data}\n" "|-"
        text_table = wtp.Table(
            "\n{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column header\n'
            "|-\n"
            f"| {edit_row_column_data}\n"
            "|-\n"
            "|}"
        )

        expected_updated_table = (
            f"{table_section}\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column header\n'
            "|-\n"
            f"| {updated_data}\n"
            "|-\n"
            "|}"
        )
        edited_table = WikiTableService().edit_table(
            text_table, table_section, edit_row_column_data, updated_row
        )
        self.assertEqual(edited_table, expected_updated_table)

    def test_get_table_row_by_column_data(self):
        column_data = " First column data"
        table = wtp.Table(
            f"""{{|class='wikitable sortable'
        |-
        ! scope="col" | First column
        |-
        |{column_data}
        |-
        |}}"""
        )
        expected_row_number = 1
        row_number = WikiTableService().get_table_row_by_column_data(table, column_data)
        self.assertEqual(expected_row_number, row_number)

    def test_get_table_row_by_column_data_fails_with__no_existing_data(self):
        column_data = "No existing data"
        table = wtp.Table(
            """{|class='wikitable sortable'
            |-
            ! scope="col" | First column
            |-
            | Column data
            |-
            |}"""
        )
        with self.assertRaises(ValueError):
            WikiTableService().get_table_row_by_column_data(table, column_data)

    def test_get_text_table(self):
        text_table = (
            "==Table section==\n"
            "{|class='wikitable sortable'\n"
            "|-\n"
            '! scope="col" | First column header\n'
            "|-\n"
            "| First column data\n"
            "|-\n"
            "|}"
        )
        table = WikiTableService().get_text_table(text_table)
        self.assertIsInstance(table, wtp.Table)

    def test_get_text_table_fails_with_text_missing_table(self):
        missing_table_text = "text"
        with self.assertRaises(ValueError):
            WikiTableService().get_text_table(missing_table_text)
