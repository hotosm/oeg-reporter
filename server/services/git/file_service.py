import os
import re

from flask import current_app

import yaml


class FileServiceError(Exception):
    """
    Custom Exception to notify callers an error occurred when handling wiki
    """

    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class FileService:
    @staticmethod
    def create_file(file_content: str, file_dir: str, filename: str) -> None:
        """
        Create a file

        Keyword arguments:
        file_content -- The contents of the updated file
        file_dir -- The directory of the file
        filename -- The name of the file

        Raises:
        ValueError -- Raised when the file already exists
        """
        try:
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            f = open(f"{file_dir}/{filename}", "x")
            f.write(file_content)
            f.close()
        except FileExistsError:
            project_id = re.search(r"\d+", filename).group(0)
            raise FileServiceError(
                f"Unable to report project {project_id}. Project already reported"
            )

    @staticmethod
    def update_file(file_content: str, file_dir: str, filename: str) -> None:
        """
        Update an existing file

        Keyword arguments:
        file_content -- The contents of the updated file
        file_dir -- The directory of the file
        filename -- The name of the file

        Raises:
        ValueError -- Raised when the file doesn't exists
        """
        try:
            f = open(f"{file_dir}/{filename}", "w+")
            f.write(file_content)
            f.close()
        except FileNotFoundError:
            project_id = re.search(r"\d+", filename).group(0)
            raise FileServiceError(
                f"Unable to update project {project_id}. Project not previously reported to git"
            )

    @staticmethod
    def get_content(file_dir):
        """
        Get the content of a file and returns it as string

        Keyword arguments:
        file_dir -- The directory of the file

        Raises:
        ValueError -- Raised when the file doesn't exists

        Returns:
        file_content -- The content of the file as string
        """
        try:
            f = open(file_dir, "r")
            file_content = f.read()
            f.close()
            return file_content
        except FileNotFoundError:
            filename = file_dir.split("/")[-1]
            project_id = re.search(r"\d+", filename).group(0)
            raise FileServiceError(f"Unable to get content from project {project_id}")

    @staticmethod
    def dict_to_yaml(yaml_dict: dict) -> str:
        """
        Parse a YAML dictionary to a string

        Keyword arguments:
        yaml_dict -- The dictionary representation of a YAML

        Returns:
        yaml_str -- The string representation of a YAML
        """
        yaml_str = yaml.dump(yaml_dict, allow_unicode=True)
        return yaml_str

    @staticmethod
    def yaml_to_dict(yaml_str: str) -> dict:
        """
        Parse a YAML string to a dictionary

        Keyword arguments:
        yaml_str -- The string representation of a YAML

        Returns:
        yaml_dict -- The dictionary representation of a YAML
        """
        yaml_dict = yaml.load(yaml_str, Loader=yaml.FullLoader)
        return yaml_dict
