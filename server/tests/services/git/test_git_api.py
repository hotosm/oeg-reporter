from server.tests.base_test_config import BaseTestCase
from unittest.mock import patch
from flask import url_for
from datetime import datetime
from server.services.git.file_service import FileServiceError


class TestGitDocumentApi(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.document_data = {
            "project": {
                "projectId": 1,
                "status": "status example",
                "name": "project name example",
                "shortDescription": "short description example",
                "changesetComment": "changeset comment example",
                "author": "project author example",
                "url": "http://example.com",
                "created": datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
                "externalSource": {
                    "imagery": "imagery example",
                    "license": "license example",
                    "instructions": "instructions example",
                    "perTaskInstructions": "per task instructions example",
                },
                "users": [{"userName": "user name example", "userId": 1}],
            },
            "organisation": {
                "name": "HOT",
                "url": "http://www.hotosm.org/",
                "description": "HOT is an international "
                "team dedicated to humanitarian "
                "action and community development "
                "through open mapping.",
            },
            "platform": {
                "name": "HOT tasking manager",
                "url": "http://www.tasks.hotosm.org/",
            },
        }
        self.success_post_message = (
            f'Document for project {self.document_data["project"]["projectId"]} created'
        )
        self.fail_post_message = (
            "Unable to write project_1.yaml in /example/path. File already exists"
        )

    @patch("server.services.git.file_service.FileService.create_file")
    @patch("server.services.git.git_service.GitService.create_document")
    def test_git_document_post(self, mocked_document, mocked_create_file):
        expected = {"Success": self.success_post_message}
        response = self.client.post(
            url_for("create_git_document"), json=self.document_data
        )
        self.assertEqual(expected, response.json)

    @patch("server.services.git.git_service.FileService.create_file")
    def test_git_document_post_fail_with_existing_file(self, mocked_create_file):
        mocked_create_file.side_effect = FileServiceError(self.fail_post_message)
        expected = {"Error": self.fail_post_message}
        response = self.client.post(
            url_for("create_git_document"), json=self.document_data
        )
        self.assertEqual(expected, response.json)
