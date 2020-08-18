from server.services.wiki.pages.templates import OrganisationPageTemplates
from server.services.wiki.pages.page_service import PageService
from server.services.wiki.mediawiki_service import MediaWikiService
from server.services.wiki.wiki_text_service import WikiTextService
from server.services.wiki.wiki_table_service import WikiTableService
from server.services.wiki.wiki_section_service import WikiSectionService
from server.models.serializers.document import OrganisationPageSchema


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
            wiki_page=(
                f"{self.templates.oeg_page}/Projects/"
                f'{organisation_page_data["project"]["name"].capitalize()}'
            ),
            text=organisation_page_data["project"]["name"].capitalize(),
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

        page_title = f"{self.templates.oeg_page}/{document_data['organisation']['name'].capitalize()}"
        token = mediawiki.get_token()
        if mediawiki.is_existing_page(page_title):
            page_text = MediaWikiService().get_page_text(page_title)
            organisation_page_table = (
                WikiSectionService()
                .get_section_table(page_text, self.templates.projects_list_section)
                .string
            )
            updated_text = WikiTableService().add_table_row(
                page_text=page_text,
                new_row=self.generate_projects_list_table_row(document_data),
                table_section_title=self.templates.projects_list_section,
                table_template=organisation_page_table,
            )
            mediawiki.edit_page(token, page_title, updated_text)
        else:
            mediawiki.create_page(token, page_title, updated_text)

    def enabled_to_report(self, document_data):
        page_title = f"{self.templates.oeg_page}/{document_data['organisation']['name'].capitalize()}"
        if MediaWikiService().is_existing_page(page_title):
            organisation_dictionary = self.wikitext_to_dict(page_title)
            serialized_organisation_page = self.parse_page_to_serializer(
                organisation_dictionary
            )

            project_names = [
                project_data["name"]
                for project_data in serialized_organisation_page["project"]
            ]

            platform_names = [
                platform_data["name"]
                for platform_data in serialized_organisation_page["platform"]
            ]

            if (
                document_data["project"]["name"].capitalize() in project_names
                and document_data["platform"]["name"] in platform_names
            ):
                return False
            else:
                return True
        else:
            return True

    def parse_page_to_serializer(self, page_dictionary: dict) -> dict:
        """
        Serialize organisation page wikitext content

        Keyword Arguments:
        page_dictionary -- Dictionary containing data from a organisation page.
                           The dictionary keys represents the section title and the value
                           represents the section text

        Returns:
        current_organisation_page -- Serialized organisation page data
        """
        current_organisation_page = {"organisation": {}, "platform": {}, "project": []}

        # Add description to organisation page data
        current_organisation_page["organisation"]["description"] = page_dictionary[
            self.templates.organisation_section
        ][self.templates.organisation_description_section].replace("\n", "")

        # Add organisation url and name to organisation page data
        (
            organisation_url,
            organisation_name,
        ) = WikiTextService().get_page_link_and_text_from_external_hyperlink(
            page_dictionary[self.templates.organisation_section][
                self.templates.organisation_link_section
            ]
        )
        current_organisation_page["organisation"]["url"] = organisation_url
        current_organisation_page["organisation"]["name"] = organisation_name

        # Add organisation projects to organisation page data
        projects_list_text = page_dictionary[self.templates.projects_section][
            self.templates.projects_list_section
        ]
        current_organisation_page["project"] = self.get_organisation_projects(
            projects_list_text
        )

        # Add organisation projects platforms to organisation page data
        current_organisation_page[
            "platform"
        ] = self.get_organisation_projects_platforms(projects_list_text)

        # Validate organisation page fields
        document_schema = OrganisationPageSchema(partial=True, only=self.page_fields)
        document_schema.load(current_organisation_page)
        return current_organisation_page

    def get_edit_page_text(
        self,
        update_fields: dict,
        current_organisation_page: dict,
        update_organisation_page: dict,
    ) -> str:
        """
        Get the text for a updated organisation page

        Keyword Arguments:
        update_fields -- Fields that are being updated
        current_organisation_page -- Dict with the current organisation page content that
                                     is being updated
        update_organisation_page -- Dict with the organisation page updated content

        Returns:
        updated_text -- Text for the updated organisation page
        """
        # Get text of a organisation page
        page_title = (
            f"{self.templates.oeg_page}/"
            f"{current_organisation_page['organisation']['name'].capitalize()}"
        )
        page_text = MediaWikiService().get_page_text(page_title)

        # Generate updated text for organisation page
        update_current_organisation_page = self.document_to_page_sections(
            update_organisation_page
        )
        sections_text = WikiTextService().generate_text_from_dict(
            page_text,
            self.templates.page_initial_section,
            update_current_organisation_page,
        )

        updated_table_fields = self.get_update_table_fields(
            update_fields, current_organisation_page
        )

        # Update organisation page text if none table field needs updated
        project_list_table = WikiSectionService().get_section_table(
            page_text, self.templates.projects_list_section
        )
        project_list_section_title = (
            f"\n=={self.templates.projects_section}==\n"
            f"==={self.templates.projects_list_section}===\n"
        )
        updated_text = (
            sections_text + project_list_section_title + project_list_table.string
        )
        if updated_table_fields:
            # Update organisation page text if any table field needs updated
            forbidden_fields = [
                self.templates.projects_list_project_author_column,
                self.templates.projects_list_project_status_column,
            ]
            project_wiki_page = WikiTextService().hyperlink_wiki_page(
                wiki_page=(
                    f"{self.templates.oeg_page}/Projects/"
                    f'{current_organisation_page["project"]["name"].capitalize()}'
                ),
                text=current_organisation_page["project"]["name"].capitalize(),
            )
            updated_project_list_table = WikiTableService().edit_table(
                project_list_table.string,
                project_list_section_title,
                updated_table_fields,
                project_wiki_page,
                forbidden_fields,
            )
            updated_text = sections_text + updated_project_list_table
        return updated_text

    def edit_page(
        self,
        update_organisation_page: dict,
        update_fields: dict,
        current_organisation_page: dict,
    ) -> None:
        """
        Edits a organisation wiki page

        Keyword arguments:
        update_organisation_page -- All required data for a project using
                         Organised Editing Guidelines
        """
        # Get the text for the updated organisation page
        mediawiki = MediaWikiService()
        token = mediawiki.get_token()
        page_title = (
            f"{self.templates.oeg_page}/"
            f"{current_organisation_page['organisation']['name'].capitalize()}"
        )
        updated_text = self.get_edit_page_text(
            update_fields, current_organisation_page, update_organisation_page
        )

        # Update the organisation page and update the page name, if necessary
        if (
            "organisation" in update_fields.keys()
            and "name" in update_fields["organisation"].keys()
            and update_fields["organisation"]["name"].capitalize()
            != current_organisation_page["organisation"]["name"].capitalize()
        ):
            new_page = (
                f"{self.templates.oeg_page}/"
                f'{update_organisation_page["organisation"]["name"].capitalize()}'
            )
            mediawiki.move_page(token=token, old_page=page_title, new_page=new_page)
            mediawiki.edit_page(token, new_page, updated_text)
        else:
            mediawiki.edit_page(token, page_title, updated_text)

    def get_update_table_fields(
        self, update_fields: dict, organisation_page_data: dict
    ):
        current_project_page_title = (
            "Organised_Editing/Activities/Auto_report/Projects/"
            f"{organisation_page_data['project']['name'].capitalize()}"
        )
        current_row_data = {
            "project_name": WikiTextService().hyperlink_wiki_page(
                current_project_page_title,
                organisation_page_data["project"]["name"].capitalize(),
            ),
            "platform": WikiTextService().hyperlink_external_link(
                organisation_page_data["platform"]["name"],
                organisation_page_data["platform"]["url"],
            ),
            "project_author": organisation_page_data["project"]["author"],
            "project_status": organisation_page_data["project"]["status"],
        }

        if "platform" in update_fields.keys() and "project" in update_fields.keys():
            update_project_name = (
                update_fields["project"]["name"]
                if "name" in update_fields["project"].keys()
                else organisation_page_data["project"]["name"]
            )
            update_project_page_title = (
                "Organised_Editing/Activities/Auto_report/Projects/"
                f"{update_project_name.capitalize()}"
            )

            update_platform_name = (
                update_fields["platform"]["name"]
                if "name" in update_fields["platform"].keys()
                else organisation_page_data["platform"]["name"]
            )
            update_platform_url = (
                update_fields["platform"]["url"]
                if "url" in update_fields["platform"].keys()
                else organisation_page_data["platform"]["url"]
            )

            update_project_author = (
                update_fields["project"]["author"]
                if "author" in update_fields["project"].keys()
                else organisation_page_data["project"]["author"]
            )
            update_project_status = (
                update_fields["project"]["status"]
                if "status" in update_fields["project"].keys()
                else organisation_page_data["project"]["status"]
            )

            update_fields = {
                self.templates.projects_list_project_name_column: {
                    "current": current_row_data["project_name"],
                    "update": WikiTextService().hyperlink_wiki_page(
                        update_project_page_title, update_project_name.capitalize()
                    ),
                },
                self.templates.projects_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": WikiTextService().hyperlink_external_link(
                        update_platform_name, update_platform_url
                    ),
                },
                self.templates.projects_list_project_author_column: {
                    "current": current_row_data["project_author"],
                    "update": update_project_author,
                },
                self.templates.projects_list_project_status_column: {
                    "current": current_row_data["project_status"],
                    "update": update_project_status,
                },
            }
            return update_fields
        elif "platform" in update_fields.keys():
            update_platform_name = (
                update_fields["platform"]["name"]
                if "name" in update_fields["platform"].keys()
                else organisation_page_data["platform"]["name"]
            )
            update_platform_url = (
                update_fields["platform"]["url"]
                if "url" in update_fields["platform"].keys()
                else organisation_page_data["platform"]["url"]
            )
            update_fields = {
                self.templates.projects_list_project_name_column: {
                    "current": current_row_data["project_name"],
                    "update": current_row_data["project_name"],
                },
                self.templates.projects_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": WikiTextService().hyperlink_external_link(
                        update_platform_name, update_platform_url
                    ),
                },
                self.templates.projects_list_project_author_column: {
                    "current": current_row_data["project_author"],
                    "update": current_row_data["project_author"],
                },
                self.templates.projects_list_project_status_column: {
                    "current": current_row_data["project_status"],
                    "update": current_row_data["project_status"],
                },
            }
            return update_fields
        elif "project" in update_fields.keys():
            update_project_name = (
                update_fields["project"]["name"]
                if "name" in update_fields["project"].keys()
                else organisation_page_data["project"]["name"]
            )
            update_project_page_title = (
                "Organised_Editing/Activities/Auto_report/Projects/"
                f"{update_project_name.capitalize()}"
            )

            update_project_author = (
                update_fields["project"]["author"]
                if "author" in update_fields["project"].keys()
                else organisation_page_data["project"]["author"]
            )
            update_project_status = (
                update_fields["project"]["status"]
                if "status" in update_fields["project"].keys()
                else organisation_page_data["project"]["status"]
            )

            update_fields = {
                self.templates.projects_list_project_name_column: {
                    "current": current_row_data["project_name"],
                    "update": WikiTextService().hyperlink_wiki_page(
                        update_project_page_title, update_project_name.capitalize()
                    ),
                },
                self.templates.projects_list_platform_name_column: {
                    "current": current_row_data["platform"],
                    "update": current_row_data["platform"],
                },
                self.templates.projects_list_project_author_column: {
                    "current": current_row_data["project_author"],
                    "update": update_project_author,
                },
                self.templates.projects_list_project_status_column: {
                    "current": current_row_data["project_status"],
                    "update": update_project_status,
                },
            }
            return update_fields
        else:
            return False

    def table_field_updated(self, update_fields: dict, current_organisation_page: dict):
        if "platform" in update_fields.keys():
            return WikiTextService().hyperlink_external_link(
                current_organisation_page["platform"]["name"],
                current_organisation_page["platform"]["url"],
            )
        elif "project" in update_fields.keys():
            return WikiTextService().hyperlink_wiki_page(
                current_organisation_page["project"]["name"].capitalize(),
                current_organisation_page["project"]["name"].capitalize(),
            )
        else:
            return False

    def get_organisation_projects(self, table_text: str):
        projects_list_table = WikiTableService().get_text_table(table_text)
        projects_list_data = projects_list_table.data(span=False)
        organisation_projects = []

        for table_row_number, table_row_data in enumerate(
            projects_list_data[1:], start=1
        ):
            project_wiki_page_hyperlink = projects_list_table.cells(
                row=table_row_number,
                column=self.templates.projects_list_project_name_column,
            ).value
            project_name = WikiTextService().get_page_link_and_text_from_wiki_page_hyperlink(
                project_wiki_page_hyperlink
            )[
                1
            ]

            project_author = projects_list_table.cells(
                row=table_row_number,
                column=self.templates.projects_list_project_author_column,
            ).value

            project_status = projects_list_table.cells(
                row=table_row_number,
                column=self.templates.projects_list_project_status_column,
            ).value

            organisation_projects.append(
                {
                    "name": project_name.strip(),
                    "author": project_author.strip(),
                    "status": project_status.strip(),
                }
            )

        return organisation_projects

    def get_organisation_projects_platforms(self, table_text):
        projects_list_table = WikiTableService().get_text_table(table_text)
        projects_list_data = projects_list_table.data(span=False)
        projects_platforms = []

        for table_row_number, table_row_data in enumerate(
            projects_list_data[1:], start=1
        ):
            platform_external_hyperlink = projects_list_table.cells(
                row=table_row_number,
                column=self.templates.projects_list_platform_name_column,
            ).value
            (
                platform_url,
                platform_name,
            ) = WikiTextService().get_page_link_and_text_from_external_hyperlink(
                platform_external_hyperlink
            )

            projects_platforms.append(
                {"name": platform_name.strip(), "url": platform_url.strip(),}  # noqa
            )
        return projects_platforms
