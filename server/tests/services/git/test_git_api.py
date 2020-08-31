from unittest.mock import patch

from flask import url_for

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.git.file_service import FileServiceError


@patch("server.services.git.git_service.git.Repo")
class TestGitDocumentApi(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.document_data = utils.document_data
        self.yaml_str = utils.document_yaml
        self.success_post_message = (
            f'Document for project {self.document_data["project"]["projectId"]} created'
        )
        self.fail_post_message = (
            f"Unable to report project {self.document_data['project']['projectId']}. "
            "Project already reported"
        )
        self.fail_patch_message = f"Unable to get content from project {self.document_data['project']['projectId']}"
        self.success_patch_message = (
            f'Document for project {self.document_data["project"]["projectId"]} updated'
        )

    @patch("server.services.git.file_service.FileService.create_file")
    @patch.dict(
        "server.services.utils.current_app.config",
        {"AUTHORIZATION_TOKEN": "secrettokenexample"},
    )
    def test_git_document_post(self, mocked_create_file, mocked_repo):
        response = self.client.post(
            url_for("create_git_document"),
            json=self.document_data,
            headers={"Authorization": "Token secrettokenexample"},
        )
        expected = {"detail": self.success_post_message}
        self.assertEqual(expected, response.json)

    @patch("server.services.git.git_service.FileService.create_file")
    @patch.dict(
        "server.services.utils.current_app.config",
        {"AUTHORIZATION_TOKEN": "secrettokenexample"},
    )
    def test_git_document_post_fail_with_existing_file(
        self, mocked_create_file, mocked_repo
    ):
        mocked_create_file.side_effect = FileServiceError(self.fail_post_message)
        response = self.client.post(
            url_for("create_git_document"),
            json=self.document_data,
            headers={"Authorization": "Token secrettokenexample"},
        )
        expected = {"detail": self.fail_post_message}
        self.assertEqual(expected, response.json)

    @patch("server.services.git.file_service.FileService.update_file")
    @patch("server.services.git.file_service.FileService.get_content")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    @patch.dict(
        "server.services.utils.current_app.config",
        {"AUTHORIZATION_TOKEN": "secrettokenexample"},
    )
    def test_git_document_patch(
        self, mocked_yaml_file, mocked_update_file, mocker_repo
    ):
        mocked_yaml_file.return_value = self.yaml_str
        update_fields = {"project": {"name": "project new name example"}}

        response = self.client.patch(
            url_for(
                "update_git_document",
                platform_name=self.document_data["platform"]["name"],
                organisation_name=self.document_data["organisation"]["name"],
                project_id=self.document_data["project"]["projectId"],
            ),
            json=update_fields,
            headers={"Authorization": "Token secrettokenexample"},
        )
        expected = {"detail": self.success_patch_message}
        self.assertEqual(expected, response.json)

    @patch("server.services.git.git_service.FileService.get_content")
    @patch.dict(
        "server.services.utils.current_app.config",
        {"AUTHORIZATION_TOKEN": "secrettokenexample"},
    )
    def test_git_document_patch_fail_withot_existing_file(
        self, mocked_get_document, mocked_repo
    ):
        mocked_get_document.side_effect = FileServiceError(self.fail_patch_message)
        response = self.client.patch(
            url_for(
                "update_git_document",
                platform_name=self.document_data["platform"]["name"],
                organisation_name=self.document_data["organisation"]["name"],
                project_id=self.document_data["project"]["projectId"],
            ),
            json={"project": {"name": "project name example"}},
            headers={"Authorization": "Token secrettokenexample"},
        )
        expected = {"detail": self.fail_patch_message}
        self.assertEqual(expected, response.json)
