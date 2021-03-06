from flask.views import MethodView
from flask import request
from flask import current_app

from marshmallow.exceptions import ValidationError
from requests.exceptions import ConnectionError

from server.services.wiki.mediawiki_service import MediaWikiServiceError
from server.services.wiki.pages.organisation_service import OrganisationPageService
from server.services.wiki.pages.project_service import ProjectPageService
from server.services.wiki.pages.overview_service import OverviewPageService
from server.services.wiki.pages.utils import generate_document_data_from_wiki_pages
from server.services.utils import check_token
from server.models.serializers.document import DocumentSchema


class WikiDocumentApi(MethodView):
    @check_token
    def post(self):
        try:
            # Validate report data
            document_schema = DocumentSchema(partial=True)
            document_schema.load(request.json)

            overview_page = OverviewPageService()
            if overview_page.enabled_to_report(request.json):
                overview_page.create_page(request.json)

            organisation_page = OrganisationPageService()
            if organisation_page.enabled_to_report(request.json):
                organisation_page.create_page(request.json)
            ProjectPageService().create_page(request.json)
            return (
                {
                    "detail": "Document for project "
                    f"{request.json['project']['projectId']} created"
                },
                201,
            )
        except MediaWikiServiceError as e:
            return {"detail": f"{str(e)}"}, 409
        except ValueError as e:
            current_app.logger.error(str(e))
            return {"detail": f"{str(e)}"}, 400
        except ConnectionError:
            return {"detail": "Error in connection with Mediawiki"}, 500
        except ValidationError as e:
            return {"detail": f"Error validating report data: {str(e)}"}, 400
        except Exception as e:
            error_msg = f"Wiki POST - unhandled error: {str(e)}"
            current_app.logger.error(error_msg)
            return {"detail": f"{str(error_msg)}"}, 500

    @check_token
    def patch(self, organisation_name: str, project_name: str):
        try:
            # Validate report data
            document_schema = DocumentSchema(partial=True)
            document_schema.load(request.json)

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
            current_app.logger.error(str(e))
            return {"detail": f"{str(e)}"}, 400
        except ValidationError as e:
            return {"detail": f"Error validating report data: {str(e)}"}, 400
        except ConnectionError:
            return {"detail": "Error in connection with Mediawiki"}, 500
        except Exception as e:
            error_msg = f"Wiki PATCH - unhandled error: {str(e)}"
            current_app.logger.error(error_msg)
            return {"detail": f"{str(error_msg)}"}, 500
