from flask.views import MethodView
from flask import request

from server.services.git.git_service import GitService
from server.models.serializers.document import DocumentSchema
from server.services.git.file_service import FileServiceError


class GitDocumentApi(MethodView):
    def post(self):
        try:
            document_schema = DocumentSchema()
            document = document_schema.load(request.json)

            platform_name = document["platform"]["name"]
            organisation_name = document["organisation"]["name"]
            project_id = document["project"]["project_id"]

            git_report = GitService(platform_name, organisation_name, project_id)
            git_report.create_document(document)
            return {"Success": f"Document for project {project_id} created"}, 201
        except FileServiceError as e:
            return {"Error": f"{str(e)}"}, 409

    def patch(self):
        return {"msg": "success"}, 201
