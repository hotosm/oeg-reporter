from flask.views import MethodView
from flask import request

from marshmallow.exceptions import ValidationError

from server.services.git.git_service import GitService
from server.models.serializers.document import DocumentSchema
from server.services.git.file_service import FileServiceError
from server.services.utils import check_token


class GitDocumentApi(MethodView):
    @check_token
    def post(self):
        try:
            document_schema = DocumentSchema()
            document = document_schema.load(request.json)

            platform_name = document["platform"]["name"]
            organisation_name = document["organisation"]["name"]
            project_id = document["project"]["project_id"]

            git_report = GitService(platform_name, organisation_name, project_id)
            git_report.create_document(document)
            return {"detail": f"Document for project {project_id} created"}, 201
        except FileServiceError as e:
            return {"detail": f"{str(e)}"}, 409
        except ValidationError as e:
            return {"detail": f"Error validating report data {str(e)}"}, 400

    @check_token
    def patch(self, platform_name: str, organisation_name: str, project_id: int):
        try:
            document_schema = DocumentSchema(partial=True)
            document = document_schema.load(request.json)
            git_report = GitService(platform_name, organisation_name, project_id)
            git_report.update_document(document_schema.dump(document))
            return {"detail": f"Document for project {project_id} updated"}, 201
        except FileServiceError as e:
            return {"detail": f"{str(e)}"}, 409
        except ValidationError as e:
            return {"detail": f"Error validating report data {str(e)}"}, 400
