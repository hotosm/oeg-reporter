from flask.views import MethodView
from flask import request

from server.services.wiki.mediawiki_service import MediaWikiServiceError
from server.services.wiki.pages.organisation_service import OrganisationPageService
from server.services.wiki.pages.project_service import ProjectPageService
from server.services.wiki.pages.overview_service import OverviewPageService
from server.services.wiki.pages.utils import generate_document_data_from_wiki_pages


class WikiDocumentApi(MethodView):
    def post(self):
        try:
            overview_page = OverviewPageService()
            overview_page.create_page(request.json)

            organisation_page = OrganisationPageService()
            organisation_page.create_page(request.json)

            project_page = ProjectPageService()
            project_page.create_page(request.json)

            return (
                {
                    "detail": "Document for project "
                    f"{request.json['project']['projectId']} created"
                },
                201,
            )
        except MediaWikiServiceError as e:
            return {"detail": f"{str(e)}"}, 409

    def patch(self, organisation_name: str, project_name: str):
        try:
            updated_document, document = generate_document_data_from_wiki_pages(
                organisation_name, project_name, request.json
            )
            OverviewPageService().edit_page(updated_document, request.json, document)
            OrganisationPageService().edit_page(
                updated_document, request.json, document
            )
            ProjectPageService().edit_page(updated_document, request.json, document)
            return {"detail": f"Document for project {project_name} reported"}, 201
        except MediaWikiServiceError as e:
            return {"detail": f"{str(e)}"}, 409
        except ValueError as e:
            return {"detail": f"{str(e)}"}, 400
