import re

import wikitextparser as wtp

from server.services.wiki.wiki_section_service import WikiSectionService


class WikiTableService:
    def get_table_column_numbers(self, table: wtp.Table) -> int:
        """
        Returns the number of columns in a table

        Keyword arguments:
        table -- The table which the number of columns is
                 being searched

        Returns:
        table_column_numbers -- The number of columns in the
                                table
        """
        header_row_index = 0
        table_data = table.data(span=False)
        table_row = table_data[header_row_index]
        table_column_numbers = len(table_row)
        return table_column_numbers

    def add_table_row(
        self,
        page_text: str,
        new_row: str,
        table_section_title: str,
        table_template: str,
    ) -> str:
        """
        Add a table with a new row to the page text

        Keyword Arguments:
        page_text -- The text which the table content is being added
        new_row -- The table row which will be added to the page text
        table_section_title -- The table section title
        table_template -- The template with the table header

        Returns:
        str -- The page text with the new table row
        """
        page_text += f"{table_template}"
        table = WikiSectionService().get_section_table(page_text, table_section_title)

        table_string = str(table)
        str_index_new_row = self.get_new_row_index(table)

        updated_table = (
            table_string[:str_index_new_row]
            + new_row
            + table_string[str_index_new_row:]
        )

        text_before_table_index = page_text.find(table_string)
        wtp_page_text = wtp.parse(page_text)

        wtp_page_text.string = page_text[0:text_before_table_index] + updated_table
        return wtp_page_text.string

    def edit_table(
        self,
        table: str,
        table_section: str,
        update_table_data: dict,
        table_row_identifier_column: str = "",
        columns_updated_in_one_row: list = [],
    ):

        """
        Edit table rows in a page text

        Keyword Arguments:
        table -- The text which the table content is being updated
        table_section_title -- The table section title
        update_table_data -- Dict with data with the update row
        table_row_identifier_column -- Identify table row that must be updated in case
                                       of there columns that must be updated only in the
                                      updated table row
        columns_updated_in_one_row -- List with columns that must be updated only in the
                                      updated table row
        Returns:
        str -- The page text with the updated table
        """
        table_string = "".join(table)
        updated_table = wtp.Table(table_string)

        table_data = updated_table.data(span=False)
        for row_number, _ in enumerate(table_data[1:], start=1):
            for edit_col in update_table_data:
                updated_table = wtp.Table(table_string)
                cell = updated_table.cells(row=row_number, column=edit_col).value
                if cell.strip() == update_table_data[edit_col]["current"].strip():
                    # Update data if column must be edited only in one row
                    if columns_updated_in_one_row:
                        if (
                            edit_col in columns_updated_in_one_row
                            and table_row_identifier_column in table_data[row_number]
                        ):
                            updated_table.cells(
                                row=row_number, column=edit_col
                            ).value = f" {update_table_data[edit_col]['update']}"
                            table_string = "".join(updated_table.string)
                        elif edit_col not in columns_updated_in_one_row:
                            updated_table.cells(
                                row=row_number, column=edit_col
                            ).value = f" {update_table_data[edit_col]['update']}"
                            table_string = "".join(updated_table.string)

                    # Update column data that can be edited in many rows
                    else:
                        updated_table.cells(
                            row=row_number, column=edit_col
                        ).value = f" {update_table_data[edit_col]['update']}"
                        table_string = "".join(updated_table.string)
        return table_section + updated_table.string

    def get_table_last_column_data(
        self, table: wtp.Table, table_column_numbers: int, row_number: int = 0
    ) -> str:
        """
        Returns data from the last column of a table row

        Keyword arguments:
        table -- The table which the data is
                 being searched
        table_column_numbers -- The number of columns of
                                the table
        row_number -- The row number of the table which
                      the data is being searched

        Returns:
        table_last_column_data -- Data from the last column
                                  of a table row
        """
        # because indexing starts at 0
        table_last_column_data = str(
            table.cells(row=row_number, column=table_column_numbers - 1)
        )
        table_last_column_data = table_last_column_data.partition("|")[-1]
        return table_last_column_data

    def get_new_row_index(self, table, row_number: int = 0):
        """
        Returns the position of the string where the new
        table row will be added

        Keyword arguments:
        table -- The table which the data is
                 being searched
        row_number -- The number of the predecessor row of the table
                      to which the new row will be added

        Returns:
        str_index_new_row -- The position of the string where the new
                             table row will be added
        """
        table_column_numbers = self.get_table_column_numbers(table)
        last_column_name = self.get_table_last_column_data(
            table, table_column_numbers, row_number
        )

        str_index_end_header = re.search(last_column_name, str(table)).span()[1]
        header_delimiter = "|-\n"
        str_index_new_row = str_index_end_header + len(header_delimiter)
        return str_index_new_row

    def get_text_table(self, text: str):
        """
        Returns the table of a text

        Keyword Arguments:
        text -- The text which the table is being searched

        Returns:
        table -- The table of the text
        """
        try:
            table = wtp.parse(text).get_tables()[0]
            return table
        except IndexError:
            raise ValueError("Error getting table from text")
