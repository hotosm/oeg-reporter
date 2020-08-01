from flask.views import MethodView
from flask import request

from server.services.wiki.mediawiki_service import MediaWikiServiceError
from server.services.wiki.pages.organisation_service import OrganisationPageService
from server.services.wiki.pages.project_service import ProjectPageService
from server.services.wiki.pages.overview_service import OverviewPageService


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
            return {"Error": f"{str(e)}"}, 409
