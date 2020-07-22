from server.tests.base_test_config import BaseTestCase
from server.services.git.git_service import GitService
from unittest.mock import patch
from server.services.git.file_service import FileService


class TestGitService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.platform_name = "TM"
        self.organisation_name = "HOT"
        self.project_id = 1
        self.report_file_repo_path = "example"
        self.report_file_folder = "github_files"

    @patch("server.services.git.git_service.git.Repo")
    def test_commit_file(self, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )

        commit_message = "Commit message"
        git_service.commit_file(commit_message)

        mocked_repo.return_value.index.commit.assert_called_once_with(commit_message)
        mocked_repo.return_value.remote.assert_called_once_with(name="origin")

    @patch.object(FileService, "create_file")
    @patch("server.services.git.git_service.git.Repo")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_REPOSITORY_PATH": "example"},
    )
    def test_create_document(self, mocked_repo, mocked_create_file):
        document_folder = (
            f"{self.report_file_repo_path}/{self.report_file_folder}/"
            f"{self.platform_name}/{self.organisation_name}"
        )
        filename = f"project_{self.project_id}.yaml"
        with patch("server.services.git.git_service.GitService"):
            git_service = GitService(
                self.platform_name, self.organisation_name, self.project_id
            )
            git_service.create_document({"project": {"name": "test name"}})

        mocked_repo.return_value.git.add.assert_called_once_with(
            [f"{document_folder}/{filename}"]
        )
