from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.services.git.git_service import GitService
from server.tests.helpers import utils


@patch("server.services.git.git_service.git.Repo")
class TestGitService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.platform_name = "TM"
        self.organisation_name = "HOT"
        self.project_id = 1
        self.report_file_repo_dir = "example"
        self.report_file_dir = "github_files"
        self.document_data = utils.document_data
        self.yaml_str = utils.document_yaml

    def test_commit_file(self, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        commit_message = "Commit message"
        git_service.commit_file(commit_message)

        mocked_repo.return_value.index.commit.assert_called_once_with(commit_message)
        mocked_repo.return_value.remote.assert_called_once_with(name="origin")

    @patch("server.services.git.git_service.FileService.create_file")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_create_document(self, mocked_create_file, mocked_repo):
        document_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{self.organisation_name}"
        )
        filename = f"project_{self.project_id}.yaml"
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        git_service.create_document({"project": {"name": "test name"}})

        yaml_example = "project:\n  name: test name\n"
        mocked_create_file.return_value = yaml_example
        mocked_create_file.assert_called_once_with(yaml_example, document_dir, filename)
        mocked_repo.return_value.git.add.assert_called_once_with(
            [f"{document_dir}/{filename}"]
        )

    def test_organisation_name_is_being_updated(self, mocked_repo):
        update_document = {
            "organisation": {"name": "updated organisation name"},
        }
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        is_organisation_name_updated = git_service.is_platform_or_org_name_being_updated(
            update_document
        )
        self.assertTrue(is_organisation_name_updated)

    def test_platform_name_is_being_updated(self, mocked_repo):
        update_document = {
            "platform": {"name": "updated platform name"},
        }
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        is_platform_name_updated = git_service.is_platform_or_org_name_being_updated(
            update_document
        )
        self.assertTrue(is_platform_name_updated)

    def test_org_or_platform_name_is_not_being_updated(self, mocked_repo):
        update_document = {"project": {"name": "project name example"}}
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        is_org_or_platform_name_updated = git_service.is_platform_or_org_name_being_updated(
            update_document
        )
        self.assertFalse(is_org_or_platform_name_updated)

    @patch("server.services.git.git_service.listdir")
    @patch("server.services.git.git_service.isfile")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_get_staged_files(self, mocked_isfile, mocked_listdir, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        mocked_listdir.return_value = ["project_1.yaml"]
        mocked_isfile.return_value = True

        filename = f"project_{self.project_id}.yaml"
        update_platform_name = "updated platform name"
        current_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{self.organisation_name}/{filename}"
        )
        update_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{update_platform_name}/{self.organisation_name}"
        )

        staged_files = git_service.get_staged_files(update_dir)
        expected_directories = tuple([[current_dir], [f"{update_dir}/{filename}"]])
        self.assertTupleEqual(expected_directories, staged_files)

    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_organisation_name_updated_dir(self, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        update_organisation_name = "updated organisation name"
        update_document = {
            "organisation": {"name": "updated organisation name"},
        }

        update_dir = git_service.get_platform_and_org_name_updated_dir(update_document)
        expected_update_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{update_organisation_name.replace(' ', '_')}"
        )
        self.assertEqual(update_dir, expected_update_dir)

    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_platform_name_updated_dir(self, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        update_platform_name = "updated platform name"
        update_document = {
            "platform": {"name": update_platform_name},
        }

        update_dir = git_service.get_platform_and_org_name_updated_dir(update_document)
        expected_update_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{update_platform_name.replace(' ', '_')}/{self.organisation_name}"
        )
        self.assertEqual(update_dir, expected_update_dir)

    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_platform_and_org_name_updated_dir(self, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        update_platform_name = "updated platform name"
        update_organisation_name = "updated organisation name"
        update_document = {
            "platform": {"name": update_platform_name},
            "organisation": {"name": update_organisation_name},
        }

        update_dir = git_service.get_platform_and_org_name_updated_dir(update_document)
        expected_update_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{update_platform_name.replace(' ', '_')}/"
            f"{update_organisation_name.replace(' ', '_')}"
        )
        self.assertEqual(update_dir, expected_update_dir)

    @patch("server.services.git.git_service.FileService.dict_to_yaml")
    def test_update_yaml_file(self, mocked_yaml, mocked_repo):
        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        update_organisation_name = "updated organisation name"
        update_project_name = "updated project name"
        update_license = "updated license"

        update_users = [
            {"userId": 1, "userName": "project author"},
            {"userId": 2, "userName": "project manager"},
        ]
        update_fields = {
            "organisation": {"name": update_organisation_name},
            "project": {
                "name": update_project_name,
                "externalSource": {"license": update_license},
                "users": update_users,
            },
        }

        git_service.update_yaml_file(update_fields, self.yaml_str)

        update_document = dict(self.document_data)
        update_document["organisation"]["name"] = update_organisation_name
        update_document["project"]["name"] = update_project_name
        update_document["project"]["externalSource"]["license"] = update_license
        update_document["project"]["users"] = update_users

        mocked_yaml.assert_called_once_with(update_document)

    @patch("server.services.git.git_service.FileService")
    @patch("server.services.git.git_service.GitService")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_update_document_with_dir_update(
        self, mocked_git_service, mocked_file_service, mocked_repo
    ):
        update_organisation_name = "updated organisation name"
        update_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{update_organisation_name.replace(' ', '_')}"
        )
        current_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{self.organisation_name}"
        )

        with patch("server.services.git.git_service.isfile", return_value=True), patch(
            "server.services.git.git_service.shutil"
        ) as mocked_shutil, patch(
            "server.services.git.git_service.listdir"
        ) as mocked_dir_files:
            git_service = GitService(
                self.platform_name, self.organisation_name, self.project_id
            )

            mocked_file_service.get_content.return_value = self.yaml_str
            mocked_file_service.yaml_to_dict.return_value = self.document_data
            mocked_git_service.update_dir.return_value = update_dir
            mocked_dir_files.return_value = ["project_1.yaml"]
            filename = f"project_{self.project_id}.yaml"
            mocked_git_service.get_staged_files.return_value = tuple(
                [[current_dir], [f"{update_dir}/{filename}"]]
            )

            git_service.update_document(
                {"organisation": {"name": update_organisation_name}}
            )

        mocked_shutil.move.assert_called_once_with(current_dir, update_dir)
        mocked_repo.return_value.git.add.assert_called_once_with(
            [f"{update_dir}/{filename}"]
        )
        mocked_repo.return_value.git.rm.assert_called_once_with(
            [f"{current_dir}/{filename}"]
        )

    @patch("server.services.git.git_service.FileService")
    @patch("server.services.git.git_service.GitService")
    @patch.dict(
        "server.services.git.git_service.current_app.config",
        {"REPORT_FILE_DIR": "example"},
    )
    def test_update_document_without_dir_update(
        self, mocked_git_service, mocked_file_service, mocked_repo
    ):
        mocked_file_service.get_content.return_value = self.yaml_str
        mocked_file_service.yaml_to_dict.return_value = self.document_data

        git_service = GitService(
            self.platform_name, self.organisation_name, self.project_id
        )
        update_project_name = "updated project name"
        git_service.update_document({"project": {"name": update_project_name}})

        current_dir = (
            f"{self.report_file_repo_dir}/{self.report_file_dir}/"
            f"{self.platform_name}/{self.organisation_name}"
        )
        filename = f"project_{self.project_id}.yaml"
        mocked_repo.return_value.git.add.assert_called_once_with(
            [f"{current_dir}/{filename}"]
        )
