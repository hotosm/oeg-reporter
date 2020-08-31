from server.services.wiki.pages.templates import OverviewPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService
from server.services.wiki.wiki_section_service import WikiSectionService
from server.models.serializers.document import OverviewPageSchema


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

        organisation_name = overview_page_data["organisation"]["name"].capitalize()
        organisation_page_title = f"{self.templates.oeg_page}/" f"{organisation_name}"

        organisation_link = wikitext.hyperlink_wiki_page(
            organisation_page_title, organisation_name
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
            f"=={self.templates.page_initial_section}==",
            overview_page_sections,
        )
        updated_text = WikiTableService().add_table_row(
            page_text=sections_text,
            new_row=self.generate_activities_list_table_row(document_data),
            table_section_title=self.templates.activities_list_section_title,
            table_template=self.templates.table_template,
        )
        if mediawiki.is_existing_page(page_title):
            page_text = MediaWikiService().get_page_text(self.templates.oeg_page)
            overview_page_table = (
                WikiSectionService()
                .get_section_table(
                    page_text, self.templates.activities_list_section_title
                )
                .string
            )
            updated_text = WikiTableService().add_table_row(
                page_text=page_text,
                new_row=self.generate_activities_list_table_row(document_data),
                table_section_title=self.templates.activities_list_section_title,
                table_template=overview_page_table,
            )
            mediawiki.edit_page(token, self.templates.oeg_page, updated_text)
        else:
            mediawiki.create_page(token, page_title, updated_text)

    def enabled_to_report(self, document_data: dict):
        if MediaWikiService().is_existing_page(self.templates.oeg_page):
            overview_dictionary = self.wikitext_to_dict(self.templates.oeg_page)
            serialized_overview_page = self.parse_page_to_serializer(
                overview_dictionary
            )

            organisation_names = [
                organisation_data["name"]
                for organisation_data in serialized_overview_page["organisation"]
            ]
            platform_names = [
                platform_data["name"]
                for platform_data in serialized_overview_page["platform"]
            ]

            if (
                document_data["organisation"]["name"].capitalize() in organisation_names
                and document_data["platform"]["name"] in platform_names
            ):
                return False
            else:
                return True
        else:
            return True

    def edit_page_text(
        self, update_fields: dict, overview_page_data: dict, document_data: dict
    ):
        page_text = MediaWikiService().get_page_text(self.templates.oeg_page)
        updated_table_fields = self.get_update_table_fields(
            update_fields, overview_page_data
        )
        if updated_table_fields:
            overview_page_table = WikiSectionService().get_section_table(
                page_text, self.templates.activities_list_section_title
            )
            project_list_section_title = (
                f"\n=={self.templates.page_initial_section}==\n"
                f"==={self.templates.activities_list_section_title}===\n"
            )
            updated_text = WikiTableService().edit_table(
                overview_page_table.string,
                project_list_section_title,
                updated_table_fields,
            )
            return updated_text
        else:
            return page_text

    def edit_page(
        self, document_data: dict, update_fields: dict, overview_page_data: dict
    ):
        mediawiki = MediaWikiService()
        token = mediawiki.get_token()

        updated_text = self.edit_page_text(
            update_fields, overview_page_data, document_data
        )
        mediawiki.edit_page(token, self.templates.oeg_page, updated_text)

    def table_field_updated(self, update_fields: dict, overview_page_data: dict):
        if "platform" in update_fields.keys():
            return WikiTextService().hyperlink_external_link(
                overview_page_data["platform"]["name"],
                overview_page_data["platform"]["url"],
            )
        elif "organisation" in update_fields.keys():
            organisation_page_title = (
                f"{self.templates.oeg_page}/"
                f"{overview_page_data['organisation']['name'].capitalize()}"
            )
            return WikiTextService().hyperlink_wiki_page(
                organisation_page_title,
                overview_page_data["organisation"]["name"].capitalize(),
            )
        else:
            return False

    def get_update_table_fields(self, update_fields, overview_page_data):
        current_organisation_page_title = (
            "Organised_Editing/Activities/Auto_report/"
            f"{overview_page_data['organisation']['name'].capitalize()}"
        )

        current_row_data = {
            "organisation": WikiTextService().hyperlink_wiki_page(
                current_organisation_page_title,
                overview_page_data["organisation"]["name"].capitalize(),
            ),
            "platform": WikiTextService().hyperlink_external_link(
                overview_page_data["platform"]["name"],
                overview_page_data["platform"]["url"],
            ),
        }
        if (
            "platform" in update_fields.keys()
            and "organisation" in update_fields.keys()
        ):
            update_platform_name = (
                update_fields["platform"]["name"]
                if "name" in update_fields["platform"].keys()
                else overview_page_data["platform"]["name"]
            )
            update_platform_url = (
                update_fields["platform"]["url"]
                if "url" in update_fields["platform"].keys()
                else overview_page_data["platform"]["url"]
            )

            update_organisation_name = (
                update_fields["organisation"]["name"].capitalize()
                if "name" in update_fields["organisation"].keys()
                else overview_page_data["organisation"]["name"].capitalize()
            )
            update_organisation_page_title = (
                "Organised_Editing/Activities/Auto_report/"
                f"{update_organisation_name.capitalize()}"
            )

            update_fields = {
                self.templates.overview_list_organisation_name_column: {
                    "current": current_row_data["organisation"],
                    "update": WikiTextService().hyperlink_wiki_page(
                        update_organisation_page_title,
                        update_organisation_name.capitalize(),
                    ),
                },
                self.templates.overview_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": WikiTextService().hyperlink_external_link(
                        update_platform_name, update_platform_url
                    ),
                },
            }
            return update_fields
        elif "platform" in update_fields.keys():
            update_platform_name = (
                update_fields["platform"]["name"]
                if "name" in update_fields["platform"].keys()
                else overview_page_data["platform"]["name"]
            )
            update_platform_url = (
                update_fields["platform"]["url"]
                if "url" in update_fields["platform"].keys()
                else overview_page_data["platform"]["url"]
            )

            update_fields = {
                self.templates.overview_list_organisation_name_column: {
                    "current": current_row_data["organisation"],
                    "update": current_row_data["organisation"],
                },
                self.templates.overview_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": WikiTextService().hyperlink_external_link(
                        update_platform_name, update_platform_url
                    ),
                },
            }
            return update_fields
        elif "organisation" in update_fields.keys():
            update_organisation_name = (
                update_fields["organisation"]["name"].capitalize()
                if "name" in update_fields["organisation"].keys()
                else overview_page_data["organisation"]["name"].capitalize()
            )
            update_organisation_page_title = (
                "Organised_Editing/Activities/Auto_report/"
                f"{update_organisation_name.capitalize()}"
            )

            update_fields = {
                self.templates.overview_list_organisation_name_column: {
                    "current": current_row_data["organisation"],
                    "update": WikiTextService().hyperlink_wiki_page(
                        update_organisation_page_title,
                        update_organisation_name.capitalize(),
                    ),
                },
                self.templates.overview_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": current_row_data["platform"],
                },
            }
            return update_fields
        else:
            return False

    def parse_page_to_serializer(self, page_dictionary: dict):
        overview_page_data = {"organisation": [], "platform": []}

        overview_page_table_text = page_dictionary[self.templates.page_initial_section][
            self.templates.activities_list_section_title
        ]
        (
            platform_list,
            organisation_list,
        ) = self.get_overview_page_platforms_and_organisations(overview_page_table_text)
        overview_page_data["organisation"] = organisation_list
        overview_page_data["platform"] = platform_list

        # Validate
        overview_page_schema = OverviewPageSchema(partial=True)
        overview_page_schema.load(overview_page_data)

        return overview_page_data

    def get_overview_page_platforms_and_organisations(
        self, overview_page_table_text: str
    ):
        overview_page_table = WikiTableService().get_text_table(
            overview_page_table_text
        )
        overview_page_table_data = overview_page_table.data(span=False)

        organisation_list = []
        platform_list = []
        wikitext = WikiTextService()

        for table_row_number, table_row_data in enumerate(
            overview_page_table_data[1:], start=1
        ):
            hyperlinked_organisation_url = overview_page_table.cells(
                row=table_row_number,
                column=self.templates.overview_list_organisation_name_column,
            ).value

            hyperlinked_platform_url = overview_page_table.cells(
                row=table_row_number,
                column=self.templates.overview_list_platform_name_column,
            ).value

            organisation_list.append(
                {
                    "name": wikitext.get_page_link_and_text_from_wiki_page_hyperlink(
                        hyperlinked_organisation_url
                    )[1]
                }
            )

            (
                platform_url,
                platform_name,
            ) = wikitext.get_page_link_and_text_from_external_hyperlink(
                hyperlinked_platform_url
            )
            platform_list.append({"name": platform_name, "url": platform_url})

        return platform_list, organisation_list
