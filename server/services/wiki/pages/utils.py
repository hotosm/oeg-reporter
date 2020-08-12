from server.services.wiki.pages.organisation_service import OrganisationPageService
from server.services.wiki.pages.project_service import ProjectPageService
from server.services.wiki.pages.overview_service import OverviewPageService
from server.services.utils import update_document


def generate_document_data_from_wiki_pages(
    organisation_name: str, project_name: str, update_fields: str
):
    """
    """
    overview_page = OverviewPageService()
    overview_dictionary = overview_page.wikitext_to_dict(
        overview_page.templates.oeg_page
    )
    overview_page.parse_page_to_serializer(overview_dictionary)

    organisation_page = OrganisationPageService()
    organisation_dictionary = organisation_page.wikitext_to_dict(
        f"{organisation_page.templates.oeg_page}/{organisation_name.capitalize()}"
    )
    organisation_page_data = organisation_page.parse_page_to_serializer(
        organisation_dictionary
    )

    project_page = ProjectPageService()
    project_dictionary = project_page.wikitext_to_dict(project_name.capitalize())
    project_page_data = project_page.parse_page_to_serializer(
        project_dictionary, project_name.capitalize()
    )

    document = {
        "organisation": organisation_page_data["organisation"],
        "platform": organisation_page_data["platform"],
    }
    for i, organisation_project in enumerate(organisation_page_data["project"]):
        if (
            organisation_project["name"].capitalize()
            == project_page_data["project"]["name"].capitalize()
        ):
            document["project"] = {
                **organisation_project,
                **project_page_data["project"],
            }
            break
    if "project" not in document.keys():
        raise ValueError(
            f"Error editing project '{project_page_data['project']['name'].capitalize()}'."
            f" Project does not belong to the organisation '{document['organisation']['name']}'."
        )
    updated_document = update_document(document, update_fields)
    return updated_document, document
