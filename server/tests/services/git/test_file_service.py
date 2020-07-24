import os
from unittest.mock import patch, mock_open

from server.tests.base_test_config import BaseTestCase
from server.services.git.file_service import FileService, FileServiceError


class TestFileService(BaseTestCase):
    def setUp(self):
        self.file_content = "file content example"
        self.filename = "project_1.yaml"
        self.file_path = os.path.dirname(__file__)
        self.yaml_dict = {
            "platform": {"name": "Tasking Manager", "url": "https://tasks.hotosm.org"}
        }
        self.yaml_str = (
            "platform:\n  name: Tasking Manager\n" "  url: https://tasks.hotosm.org"
        )

    def test_get_content(self):
        open_mock = mock_open(read_data=self.file_content)
        with patch("server.services.git.file_service.open", open_mock):
            get_content_result = FileService.get_content(self.filename)

        expected = self.file_content
        open_mock.assert_called_with(self.filename, "r")
        open_mock.return_value.read.assert_called_once_with()
        self.assertEqual(expected, get_content_result)

    def test_get_content_fails_without_file(self):
        open_mock = mock_open()
        open_mock.side_effect = FileNotFoundError

        with patch("server.services.git.file_service.open", open_mock):
            with self.assertRaises(FileServiceError):
                FileService.get_content(self.filename)

    def test_update_file(self):
        open_mock = mock_open()
        with patch("server.services.git.file_service.open", open_mock):
            FileService.update_file(self.file_content, self.file_path, self.filename)

        open_mock.assert_called_with(f"{self.file_path}/{self.filename}", "w+")
        open_mock.return_value.write.assert_called_once_with(self.file_content)
        open_mock.return_value.close.assert_called_once_with()

    def test_update_file_fails_without_file(self):
        open_mock = mock_open()
        open_mock.side_effect = FileNotFoundError

        with patch("server.services.git.file_service.open", open_mock):
            with self.assertRaises(FileServiceError):
                FileService.update_file(
                    self.file_content, self.file_path, self.filename
                )

    def test_create_file_fails_with_existing_file(self):
        open_mock = mock_open()
        open_mock.side_effect = FileExistsError

        with patch("server.services.git.file_service.open", open_mock):
            with self.assertRaises(FileServiceError):
                FileService.create_file(
                    self.file_content, self.file_path, self.filename
                )

    @patch("server.services.git.file_service.os.path.exists", return_value=False)
    @patch("server.services.git.file_service.os.makedirs", return_value=False)
    def test_create_file(self, mocked_path, mocked_dir):
        open_mock = mock_open()
        non_existing_path = "~/Documents"

        with patch("server.services.git.file_service.open", open_mock):
            FileService.create_file(self.file_content, non_existing_path, self.filename)
        open_mock.assert_called_with(f"{non_existing_path}/{self.filename}", "x")
        open_mock.return_value.write.assert_called_once_with(self.file_content)
        open_mock.return_value.close.assert_called_once_with()

        mocked_path.assert_called_once_with(non_existing_path)
        mocked_dir.assert_called_once_with(non_existing_path)

    def test_dict_to_yaml(self):
        yaml_str = FileService.dict_to_yaml(self.yaml_dict)
        self.assertIsInstance(yaml_str, str)

    def test_yaml_to_dict(self):
        yaml_dict = FileService.yaml_to_dict(self.yaml_str)

        self.assertIsInstance(yaml_dict, dict)
        self.assertDictEqual(self.yaml_dict, yaml_dict)
